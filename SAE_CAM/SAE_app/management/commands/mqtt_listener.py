import json
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection

from SAE_app.models import Capteur, Data


class Command(BaseCommand):
    help = "Teste la DB distante, puis démarre un listener MQTT et insère les messages en base via l'ORM Django"

    def handle(self, *args, **options):
        # 1️⃣ Affiche et teste la config DB
        self.stdout.write("⚙️ DB config:")
        for k, v in settings.DATABASES['default'].items():
            self.stdout.write(f"   {k}: {v!r}")

        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS("✅ Connexion à la DB OK"))
        except Exception as e:
            raise CommandError(f"❌ Impossible de se connecter à la DB : {e}")

        # 2️⃣ Démarrage du listener MQTT
        self.stdout.write(self.style.SUCCESS("🟢 Démarrage du MQTT listener…"))

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS("🔌 Connecté au broker MQTT (rc=0)"))
                client.subscribe("IUT/Colmar2025/SAE2.04/#")
            else:
                raise CommandError(f"Erreur de connexion MQTT (rc={rc})")

        def on_message(client, userdata, msg):
            raw = msg.payload.decode()
            self.stdout.write(f"📥 Reçu : {raw}")

            # 3️⃣ Détection JSON vs clé=valeur
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # fallback parsing clé=valeur
                try:
                    items = dict(x.split("=", 1) for x in raw.split(","))
                except ValueError:
                    self.stdout.write(self.style.ERROR("❌ Payload mal formé, impossible de parser."))
                    return
                data = {k.lower(): v for k, v in items.items()}
                if "time" in data:
                    data["heure"] = data.pop("time")
            else:
                # normalisation du JSON
                # timestamp → datetime object
                ts = data.pop("timestamp", None)
                if ts:
                    data["dt_obj"] = datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
                # renommer les clefs pour matcher vos champs
                if "room" in data:
                    data["piece"] = data.pop("room")
                # house → emplacement si vous voulez
                if "house" in data:
                    data["emplacement"] = data.pop("house")

            # 4️⃣ Construire le datetime
            if "dt_obj" in data:
                dt = data["dt_obj"]
            else:
                date_str = data.get("date", "")
                heure_str = data.get("heure", "")
                if not date_str or not heure_str:
                    self.stdout.write(self.style.ERROR("❌ Clés 'date' ou 'heure' manquantes."))
                    return
                fmt = "%d/%m/%Y %H:%M:%S" if "/" in date_str else "%Y-%m-%d %H:%M:%S"
                try:
                    dt = datetime.strptime(f"{date_str} {heure_str}", fmt).replace(tzinfo=timezone.utc)
                except ValueError as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erreur format date/heure : {e}"))
                    return

            # 5️⃣ Parser la température
            raw_temp = str(data.get("temp", "")).replace(",", ".")
            try:
                temp_val = float(raw_temp)
            except ValueError:
                self.stdout.write(self.style.ERROR(f"❌ Impossible de convertir temp={raw_temp}"))
                return

            # 6️⃣ Update or create Capteur
            cap_id = data.get("id")
            default_name = data.get("nom") or f"capteur_{cap_id}"
            capteur, created = Capteur.objects.update_or_create(
                pk=cap_id,
                defaults={
                    "nom": default_name,
                    "piece": data.get("piece", ""),
                    "emplacement": data.get("emplacement", ""),
                },
            )
            verb = "Créé" if created else "Mis à jour"
            self.stdout.write(f"   • Capteur {verb} : {capteur.nom} ({capteur.id})")

            # 7️⃣ Insérer la Data avec la température
            Data.objects.create(
                id_data=capteur,
                date_heure=dt,
                temp=str(temp_val)
            )
            self.stdout.write(self.style.SUCCESS(
                f"   ✔️ Donnée insérée à {dt.isoformat()} – temp={temp_val}"
            ))

        # 8️⃣ Configuration et connexion MQTT avec retry
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        host, port, keepalive = "test.mosquitto.org", 1883, 60
        for attempt in range(1, 6):
            try:
                client.connect(host, port, keepalive)
                break
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f"❌ Tentative {attempt}/5 échouée : {e}"
                ))
                time.sleep(5)
        else:
            raise CommandError("Impossible de se connecter au broker MQTT après 5 tentatives")

        # 9️⃣ Boucle d'écoute
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            self.stdout.write(self.style.NOTICE("🛑 Arrêt du listener MQTT"))