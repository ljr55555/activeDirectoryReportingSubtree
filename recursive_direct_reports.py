################################################################################
#  This script lists a manager and their reporting subtree based
# on the directReport backlinked attribute in Active Directory. 
################################################################################
import sys
import getopt
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, AUTO_BIND_NO_TLS, SUBTREE
from ldap3.core.exceptions import LDAPCursorError
from config import strLDAPHost, strBindFQDN, strBindPassword, strSearchBase

def printUsage():
	print("This program generates a file with all subordinates to a manager (the entire sub-tree of the manager's reporting structure).\n")
	print(f"Usage: \n\tpython {sys.argv[0]} -u e#######\n\t-u\tLogon ID of top level manager for report")


def findRecursiveReports(ldapConn, strUserFQDN):
	ldapConn.search(strUserFQDN, '(objectClass=user)', attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])
	for ldapRecord in ldapConn.entries:
		print(f"{ldapRecord.sAMAccountName}\t{ldapRecord.displayName}")
		try:
			strSubReportFQDNs = ldapRecord.directReports.values
		except:
			strSubReportFQDNs  = None

		if strSubReportFQDNs is not None:
			for strSubReportFQDN in strSubReportFQDNs:
				findRecursiveReports(ldapConn, strSubReportFQDN)


# Get args and find the starting point for the reporting subtree
try:
	opts, args = getopt.getopt(sys.argv[1:], 'u:h', ['user=', 'help'])
except:
	printUsage()

strBaseUser = None
for opt, arg in opts:
	if opt in ('-h', '--help'):
		printUsage()
	elif opt in ('-u', '--user'):
		strBaseUser = arg
	else:
		printUsage()

if strBaseUser is None:
	printUsage()
else:
	server = Server(strLDAPHost, get_info=ALL)
	conn = Connection(server, user=strBindFQDN, password=strBindPassword, auto_bind=True)

	conn.search(strSearchBase, f'(sAMAccountName={strBaseUser})', attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES])
	for e in conn.entries:
		print(f"{e.sAMAccountName}\t{e.displayName}")
		try:
			strReportFQDNs = e.directReports.values
		except LDAPCursorError:
			strReportFQDNs = None
			print(f"No direct reports found for {strBaseUser}")

		if strReportFQDNs is not None:
			for strBaseReportFQDN in strReportFQDNs:
				findRecursiveReports(conn, strBaseReportFQDN)

		print("\n")

