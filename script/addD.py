import requests
from pyzabbix import ZabbixAPI

# Connexion à NetBox
NETBOX_API_URL = "http://51.254.199.129:8080/api/"
TOKEN = "6f85af1afefd1b8d71bf33b274fd68d08f76db75"  # Token NetBox
headers = {"Authorization": f"Token {TOKEN}"}

# Connexion à Zabbix
zabbix_url = "https://monitoring.myitcrew.io/zabbix"
zabbix_user = "Admin"
zabbix_password = "mhFrjsaP6k7cmG43bUVF"
API_TOKEN="208347aabf1d810a2b029200dd366371f999009eb3d25cefbf5fe3bce932115b"
zapi = ZabbixAPI(zabbix_url)
#zapi.login(zabbix_user, zabbix_password)
zapi.session.headers.update({"Authorization": f"Bearer {API_TOKEN}"})
print("Connexion réussie à Zabbix API")

# Fonction pour récupérer l'ID d'un groupe par nom
def get_group_id(group_name):
    group = zapi.hostgroup.get(filter={"name": group_name}, output=["groupid"])
    if group:
        return group[0]['groupid']
    else:
        raise ValueError(f"Groupe '{group_name}' non trouvé.")

# Fonction pour récupérer l'ID d'un template par nom
def get_template_id(template_name):
    template = zapi.template.get(filter={"host": template_name}, output=["templateid"])
    if template:
        return template[0]['templateid']
    else:
        raise ValueError(f"Template '{template_name}' non trouvé.")
# Fonction pour vérifier l'existance des serveurs sur zabbix
def host_exists(hostname):
    hosts = zapi.host.get(filter={"host": hostname}, output=["hostid"])
    return len(hosts) > 0
# Obtenir les IDs du groupe et du template
group_name = "Linux servers"
template_name = "Linux by Zabbix agent"

group_id = get_group_id(group_name)
template_id = get_template_id(template_name)
#print(group_id)
#print(template_id)
# Fonction pour ajouter un hôte dans Zabbix
def add_host_to_zabbix(hostname, ip_address, group_id, template_id):
    if host_exists(hostname):
        print(f"Hôte '{hostname}' existe déjà dans Zabbix. Aucun ajout nécessaire.")
        return
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
        print(f"Hôte '{hostname}' ajouté avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'ajout de l'hôte '{hostname}': {e}")
# Récupérer les périphériques depuis NetBox
response = requests.get(f"{NETBOX_API_URL}dcim/devices/", headers=headers)
if response.status_code == 200:
    devices = response.json()
    for device in devices['results']:
        hostname = device.get('name', 'Nom non défini')
        ip_address = device.get('primary_ip4', {}).get('address', '').split('/')[0]
        if hostname and ip_address:
            add_host_to_zabbix(hostname, ip_address, group_id, template_id)
else:
    print(f"Erreur lors de l'accès à NetBox : {response.status_code}")
