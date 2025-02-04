import requests
from pyzabbix import ZabbixAPI
from extras.scripts import Script

class SyncDeviceToZabbix(Script):
    class Meta:
        name = "Sync New Device to Zabbix"
        description = "Ajoute automatiquement un device créé sur NetBox à Zabbix."
    
    def run(self, data, commit):
        # Récupérer les informations du device
        device = data['device']
        hostname = device.name
        ip_address = device.primary_ip4.address.split('/')[0] if device.primary_ip4 else None

        if not ip_address:
            self.log_failure(f"Le device '{hostname}' n'a pas d'adresse IP définie.")
            return

        # Connexion à l'API Zabbix
        zabbix_url = "https://monitoring.myitcrew.io/zabbix"
        API_TOKEN = "208347aabf1d810a2b029200dd366371f999009eb3d25cefbf5fe3bce932115b"
        zapi = ZabbixAPI(zabbix_url)
        zapi.session.headers.update({"Authorization": f"Bearer {API_TOKEN}"})

        # Récupérer l'ID du groupe et du template
        group_name = "Linux servers"
        template_name = "Linux by Zabbix agent"

        group = zapi.hostgroup.get(filter={"name": group_name}, output=["groupid"])
        template = zapi.template.get(filter={"host": template_name}, output=["templateid"])

        if not group or not template:
            self.log_failure("Groupe ou Template introuvable dans Zabbix.")
            return

        group_id = group[0]['groupid']
        template_id = template[0]['templateid']

        # Vérifier si l'hôte existe déjà
        existing_hosts = zapi.host.get(filter={"host": hostname}, output=["hostid"])
        if existing_hosts:
            self.log_info(f"Hôte '{hostname}' existe déjà dans Zabbix.")
            return

        # Ajouter le device à Zabbix
        try:
            zapi.host.create(
                host=hostname,
                interfaces=[{
                    "type": 1, "main": 1, "useip": 1,
                    "ip": ip_address, "dns": "", "port": "10050"
                }],
                groups=[{"groupid": group_id}],
                templates=[{"templateid": template_id}]
            )
            self.log_success(f"Hôte '{hostname}' ajouté avec succès à Zabbix.")
        except Exception as e:
            self.log_failure(f"Erreur lors de l'ajout de l'hôte '{hostname}': {e}")
