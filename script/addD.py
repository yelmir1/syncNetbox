import requests
from pyzabbix import ZabbixAPI
from extras.scripts import Script, StringVar

NETBOX_API_URL = "http://51.254.199.129:8080/api/"
TOKEN = "6f85af1afefd1b8d71bf33b274fd68d08f76db75"
ZABBIX_URL = "https://monitoring.myitcrew.io/zabbix"
API_TOKEN = "208347aabf1d810a2b029200dd366371f999009eb3d25cefbf5fe3bce932115b"

class AddDeviceToZabbix(Script):
    class Meta:
        name = "Add Device to Zabbix"
        description = "Ajoute un device NetBox à Zabbix automatiquement"

    device_name = StringVar(description="Nom du device")
    ip_address = StringVar(description="Adresse IP du device")

    def run(self, data, commit):
        headers = {"Authorization": f"Token {TOKEN}"}
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.session.headers.update({"Authorization": f"Bearer {API_TOKEN}"})

        self.log_success("Connexion réussie à Zabbix API")

        hostname = data['device_name']
        ip_address = data['ip_address']

        if not hostname or not ip_address:
            self.log_failure("Nom d'hôte ou adresse IP manquant.")
            return

        # Vérifier si l'hôte existe
        hosts = zapi.host.get(filter={"host": hostname}, output=["hostid"])
        if hosts:
            self.log_info(f"L'hôte '{hostname}' existe déjà dans Zabbix.")
            return

        # Récupérer les IDs du groupe et du template
        group_name = "Linux servers"
        template_name = "Linux by Zabbix agent"

        group = zapi.hostgroup.get(filter={"name": group_name}, output=["groupid"])
        template = zapi.template.get(filter={"host": template_name}, output=["templateid"])

        if not group or not template:
            self.log_failure("Groupe ou Template non trouvé dans Zabbix.")
            return
        
        group_id = group[0]["groupid"]
        template_id = template[0]["templateid"]

        # Ajouter l'hôte à Zabbix
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
