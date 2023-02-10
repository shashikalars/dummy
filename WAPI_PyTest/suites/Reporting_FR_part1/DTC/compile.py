import py_compile
var = bool(py_compile.compile("test_MG_dns_traffic_control_resource_pool_availability_trend.py"))
print var;
if (not(py_compile.compile("test_MG_dns_traffic_control_resource_pool_availability_trend.py"))):
	print("\n No problem \n");
