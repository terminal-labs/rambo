def random_tag
  host = `hostname`.strip # Get the hostname from the shell and removing trailing \n
  Dir.mkdir('.tmp') unless File.exists?('.tmp')
  random_tag_filename = '.tmp/random_tag'
  if !File.file?(random_tag_filename)
    tag = host + '-' + SecureRandom.urlsafe_base64(4)
    File.write(random_tag_filename, tag)
  else
    tag = File.read(random_tag_filename)
  end
  return tag
end

def read_provider_file
  Dir.mkdir('.tmp') unless File.exists?('.tmp')
  provider_name = '.tmp/provider'
  if !File.file?(provider_name)
    return false
  else
    provider=''
    File.open(provider_name, 'r') do |f|
     provider = f.read()
    end
    return provider
  end
end

def write_provider_file(provider)
  Dir.mkdir('.tmp') unless File.exists?('.tmp')
  provider_name = '.tmp/provider'
  File.write(provider_name, provider)
end
