import sys
from pkg_resources import resource_filename
pkg_path = resource_filename('mechanisms', 'core')
pkg_path = pkg_path.replace('/mechanisms/core', '')
sys.path.append(pkg_path)
