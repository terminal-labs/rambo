def random_tag
  host = `hostname`.strip # Get the hostname from the shell and removing trailing \n
  tmp_dir = ENV[PROJECT_NAME.upcase + '_TMP'] || File.join(File.basename(Dir.pwd), '.tmp')
  Dir.mkdir(tmp_dir) unless Dir.exist?(tmp_dir)
  random_tag_path = File.join(tmp_dir, 'random_tag')
  if File.file?(random_tag_path)
    tag = File.read(random_tag_path)
  else
    tag = host + '-' + File.basename(File.dirname(tmp_dir)) + '-' + SecureRandom.hex(6)
    File.write(random_tag_path, tag)
  end
  puts tag
  return tag
end

def read_provider_file
  tmp_dir = ENV[PROJECT_NAME.upcase + '_TMP'] || File.join(File.basename(Dir.pwd), '.tmp')
  provider_path = File.join(tmp_dir, 'provider')
  if File.file?(provider_path)
    provider=''
    File.open(provider_path, 'r') do |f|
     provider = f.read()
    end
    return provider
  else
    return false
  end
end

def write_provider_file(provider)
  tmp_dir = ENV[PROJECT_NAME.upcase + '_TMP'] || File.join(File.basename(Dir.pwd), '.tmp')
  provider_path = File.join(tmp_dir, 'provider')
  File.write(provider_path, provider)
end
