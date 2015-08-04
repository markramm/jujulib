from jujulib.system import System

def test_system_instantiation(): 
	s = System()
	assert isinstance(s,System)

def test_connect():
	assert False