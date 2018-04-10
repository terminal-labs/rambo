import salt.config
import salt.cloud

opts = salt.config.master_config('/home/user/Desktop/do_configs/master')

#opts["pki_dir"] = "/home/user/Desktop/pkikeys"
#opts["cachedir"] = "/home/user/Desktop/cache/salt/master"
#print(opts['providers']['do'])


client = salt.cloud.CloudClient("/home/user/Desktop/do_configs/cloud", config_dir="/home/user/Desktop/do_configs/")

#print(client.list_sizes(provider='do'))
#print(client.profile("ubuntu-14", names=['minion01',]))
print(client.destroy(names=['minion01',]))