from configparser import ConfigParser
from pathlib import Path


def load_config() -> dict:
	config_file = Path('config.ini')
	
	if not config_file.exists():
		print('Configuration file not found, Card Generator will use the default configuration.')
		return None
	
	_config = ConfigParser()
	_config.optionxform = str
	_config.read(config_file)
	
	_parsed_config = {}
	
	for section in _config.sections():
		_parsed_config[section] = {}
		for option in _config.options(section):
			_parsed_config[section][option] = eval(_config.get(section, option))
	
	return _parsed_config