def random_tag
  host = `hostname`.strip # Get the hostname from the shell and removing trailing \n
  tmp_dir = get_env_var_rb('TMPDIR_PATH') || File.join(Dir.pwd, '.' + PROJECT_NAME + '-tmp')
  Dir.mkdir(tmp_dir) unless Dir.exist?(tmp_dir)
  random_tag_path = File.join(tmp_dir, 'random_tag')
  if File.file?(random_tag_path)
    tag = File.read(random_tag_path)
  else
    tag = host + '-' + File.basename(File.dirname(tmp_dir)) + '-' + SecureRandom.hex(6)
    File.write(random_tag_path, tag)
  end
  return tag
end

def read_provider_file
  tmp_dir = get_env_var_rb('TMPDIR_PATH') || File.join(Dir.pwd, '.' + PROJECT_NAME + '-tmp')
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
  tmp_dir = get_env_var_rb('TMPDIR_PATH') || File.join(Dir.pwd,  '.' + PROJECT_NAME + '-tmp')
  provider_path = File.join(tmp_dir, 'provider')
  File.write(provider_path, provider)
end

def set_env_var_rb(name, value)
  # Set an environment variable in all caps that is prefixed with the name of the project
  ENV[PROJECT_NAME.upcase + "_" + name.upcase] = value
end

def get_env_var_rb(name)
  # Get an environment variable in all caps that is prefixed with the name of the project
  return ENV[PROJECT_NAME.upcase + "_" + name.upcase]
end
