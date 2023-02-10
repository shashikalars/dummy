package com.cisco.pxgrid.samples.ise;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Calendar;
import java.util.List;
import java.util.Scanner;

import com.cisco.pxgrid.Configuration;
import com.cisco.pxgrid.GCLException;
import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.GridConnection.Listener;
import com.cisco.pxgrid.ReconnectionManager;
import com.cisco.pxgrid.TLSConfiguration;
import com.cisco.pxgrid.model.core.GenericAttribute;
import com.cisco.pxgrid.model.core.GenericAttributeValueType;
import com.cisco.pxgrid.model.core.IPInterfaceIdentifier;
import com.cisco.pxgrid.model.core.Subnet;
import com.cisco.pxgrid.model.core.SubnetContentFilter;
import com.cisco.pxgrid.model.identity.SXPBinding;
import com.cisco.pxgrid.model.net.DevicePortIdentifier;
import com.cisco.pxgrid.model.net.Port;
import com.cisco.pxgrid.model.net.PostureAssessment;
import com.cisco.pxgrid.model.net.RADIUSAVPair;
import com.cisco.pxgrid.model.net.Session;
import com.cisco.pxgrid.model.net.User;

/*
 * Example to run directly from java command line
 * -Dlogback.configurationFile="src/main/samples/conf" -Dsmack.debugEnabled=true -DPXGRID_HOSTNAMES="pxgrid-001" -DPXGRID_USERNAME="alei02" -DPXGRID_GROUP="ANC" -DPXGRID_TRUSTSTORE_FILENAME="src/main/samples/certs/rootSample.jks" -DPXGRID_TRUSTSTORE_PASSWORD="cisco123" -DPXGRID_KEYSTORE_FILENAME="src/main/samples/certs/clientSample1.jks" -DPXGRID_KEYSTORE_PASSWORD="cisco123"
 */
public class SampleHelper {
	protected final static String PROP_HOSTNAMES="PXGRID_HOSTNAMES";
	protected final static String PROP_USERNAME="PXGRID_USERNAME";
	protected final static String PROP_GROUP="PXGRID_GROUP";
	protected final static String PROP_DESCRIPTION="PXGRID_DESCRIPTION";
	protected final static String PROP_KEYSTORE_FILENAME="PXGRID_KEYSTORE_FILENAME"; 
	protected final static String PROP_KEYSTORE_PASSWORD="PXGRID_KEYSTORE_PASSWORD"; 
	protected final static String PROP_TRUSTSTORE_FILENAME="PXGRID_TRUSTSTORE_FILENAME"; 
	protected final static String PROP_TRUSTSTORE_PASSWORD="PXGRID_TRUSTSTORE_PASSWORD";

	private String version;
	private String hostnames;
	private String username;
	private String group;
	private String description;
	
	private String keystoreFilename;
	private String keystorePassword;
	private String truststoreFilename;
	private String truststorePassword;
	
	private boolean connected;
	private GridConnection grid;
	private ReconnectionManager reconnection;
	private Scanner scanner;

	public SampleHelper() throws ParseException, GeneralSecurityException, IOException {
		load();
		print();
		scanner = new Scanner(System.in);
	}
	
	private void keystoreLoadTest(String filename, String password) throws GeneralSecurityException, IOException {
		KeyStore ks = KeyStore.getInstance("JKS");
		ks.load(new FileInputStream(filename), password.toCharArray());
	}	

	private void load() throws ParseException, GeneralSecurityException, IOException {
		
		version = GridConnection.class.getPackage().getImplementationVersion();
		
		hostnames = System.getProperty(PROP_HOSTNAMES);
		username = System.getProperty(PROP_USERNAME);
		group = System.getProperty(PROP_GROUP);
		description = System.getProperty(PROP_DESCRIPTION);
		
		keystoreFilename = System.getProperty(PROP_KEYSTORE_FILENAME);
		keystorePassword = System.getProperty(PROP_KEYSTORE_PASSWORD);
		truststoreFilename = System.getProperty(PROP_TRUSTSTORE_FILENAME);
		truststorePassword = System.getProperty(PROP_TRUSTSTORE_PASSWORD);

		if (hostnames == null || hostnames.isEmpty()) throw new IllegalArgumentException("Missing " + PROP_HOSTNAMES);
		if (username == null || username.isEmpty()) throw new IllegalArgumentException("Missing " + PROP_USERNAME);
		if (keystoreFilename == null || keystoreFilename.isEmpty()) throw new IllegalArgumentException("Missing " + PROP_KEYSTORE_FILENAME);
		if (keystorePassword == null || keystorePassword.isEmpty()) throw new IllegalArgumentException("Missing " + PROP_KEYSTORE_PASSWORD);
		if (truststoreFilename == null || truststoreFilename.isEmpty()) throw new IllegalArgumentException("Missing " + PROP_TRUSTSTORE_FILENAME);
		if (truststorePassword == null || truststorePassword.isEmpty()) throw new IllegalArgumentException("Missing " + PROP_TRUSTSTORE_PASSWORD);

		// TODO Trim
		
		if (group != null && group.isEmpty()) {
			group = null;
		}
		if (description != null) {
			if (description.isEmpty()) description = null;
			else description = description.trim();
		}
		
		keystoreLoadTest(keystoreFilename, keystorePassword);
		keystoreLoadTest(truststoreFilename, truststorePassword);
	}
	
	private Configuration createConfig() throws ParseException, GeneralSecurityException, IOException {
		// TODO hostnames trimming

		TLSConfiguration config = new TLSConfiguration();
		config.setHosts(hostnames.split(","));
		config.setUserName(username);
		
		if(group != null && !group.isEmpty()){
			config.setGroups(Arrays.asList(group.split(",")));
		}
		config.setDescription(description);
		config.setKeystorePath(keystoreFilename);
		config.setKeystorePassphrase(keystorePassword);
		config.setTruststorePath(truststoreFilename);
		config.setTruststorePassphrase(truststorePassword);
		
		return config;
	}
	
	private void print() {
		System.out.println("------- properties -------");
		System.out.println("  version=" + version);
		System.out.println("  hostnames=" + hostnames);
		System.out.println("  username=" + username);
		System.out.println("  group=" + group);
		System.out.println("  description=" + description);
		System.out.println("  keystoreFilename=" + keystoreFilename);
		System.out.println("  keystorePassword=" + keystorePassword);
		System.out.println("  truststoreFilename=" + truststoreFilename);
		System.out.println("  truststorePassword=" + truststorePassword);
		System.out.println("--------------------------");
	}

	public GridConnection connect() throws GCLException, ParseException, GeneralSecurityException, IOException, InterruptedException {
		Configuration config = createConfig();
		grid = new GridConnection(config);
		grid.addListener(new MyListener());
		grid.connect();
		return grid;
	}
	
	public GridConnection connectWithReconnectionManager() throws GCLException, ParseException, GeneralSecurityException, IOException, InterruptedException {
		Configuration config = createConfig();
		grid = new GridConnection(config);
		grid.addListener(new MyListener());
		reconnection = new ReconnectionManager(grid);
		reconnection.setRetryMillisecond(2000);
		reconnection.start();
		synchronized (this) {
			if (!connected) this.wait();
		}
		return grid;
	}
	
	public void disconnect() throws GCLException {
		if (reconnection != null) {
			reconnection.stop();
			reconnection = null;
		}
		else if (grid != null) {
			grid.disconnect();
			grid = null;
		}
	}
	
	public String prompt(String msg) {
		System.out.print(msg);
		String value = scanner.nextLine();
		if ("".equals(value)) return null;
		return value;
	}
	
	public Calendar promptDate(String msg) throws ParseException {
		SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
		
		System.out.print(msg);
		String value = scanner.nextLine();
		if ("".equals(value)) return null;

		Calendar cal = Calendar.getInstance();
		
		try {
			cal.setTime(format.parse(value));
		} catch (ParseException e) {
			
		}
		
		return cal;
	}
	
	public SubnetContentFilter promptIpFilters(String msg) {
		System.out.print(msg);
		String line = scanner.nextLine();
		if ("".equals(line)) return null;

		SubnetContentFilter filter = new SubnetContentFilter();
		String[] values = line.split(",");
		for (String value : values) {
			String[] split = value.trim().split("/");
			String address = split[0];
			String prefixOrMask = split[1];
			Subnet s = new Subnet();
			s.setNetworkIp(address);
			if (prefixOrMask.indexOf(':') == -1 && prefixOrMask.indexOf('.') == -1) {
				s.setPrefix(prefixOrMask);
			}
			else {
				s.setNetmask(prefixOrMask);
			}
			filter.getSubnets().add(s);
		}
		return filter;
	}

	public static void print(Session session) {
		System.out.print("Session={");
		
		List<IPInterfaceIdentifier> intfIDs = session.getInterface().getIpIntfIDs();
		System.out.print("ip=[");
		for (int i = 0; i < intfIDs.size(); i++) {
			if (i > 0) System.out.print(",");
			System.out.print(intfIDs.get(i).getIpAddress());
		}
		System.out.print("]");

		System.out.print(", Audit Session Id=" +session.getGid());
		User user = session.getUser();
		if (user != null) {
			System.out.print(", User Name=" + user.getName());
			System.out.print(", AD User DNS Domain=" + user.getADUserDNSDomain());
			System.out.print(", AD Host DNS Domain=" + user.getADHostDNSDomain());
			System.out.print(", AD User NetBIOS Name=" + user.getADUserNetBIOSName());
			System.out.print(", AD Host NETBIOS Name=" + user.getADHostNetBIOSName());
		}

		List<String> macs = session.getInterface().getMacAddresses();
		if (macs != null && macs.size() > 0) {
			System.out.print(", Calling station id=" + macs.get(0));
		}

		System.out.print(", Session state=" + session.getState());			
		//System.out.print(", Epsstatus=" + session.getEPSStatus());
		System.out.print(", ANCstatus=" + session.getANCStatus());
		System.out.print(", Security Group=" +  session.getSecurityGroup());
		System.out.print(", Endpoint Profile=" +  session.getEndpointProfile());

		// Port and NAS Ip information
		DevicePortIdentifier deviceAttachPt = session.getInterface().getDeviceAttachPt();
		if (deviceAttachPt != null) {
			IPInterfaceIdentifier deviceMgmtIntfID = deviceAttachPt.getDeviceMgmtIntfID();
			if (deviceMgmtIntfID != null) {
				System.out.print(", NAS IP=" + deviceAttachPt.getDeviceMgmtIntfID().getIpAddress());
			}
			Port port = deviceAttachPt.getPort();
			if (port != null) {
				System.out.print(", NAS Port=" + port.getPortId());
			}
		}
		
		List<RADIUSAVPair> radiusAVPairs = session.getRADIUSAttrs();
		if (radiusAVPairs != null && !radiusAVPairs.isEmpty()) {
			System.out.print(", RADIUSAVPairs=[");
			for(RADIUSAVPair p : radiusAVPairs) {
				System.out.print(" " + p.getAttrName() + "=" + p.getAttrValue() );
			}
			System.out.print("]");
		}
		
		// Posture Info
		List<PostureAssessment> postures = session.getAssessedPostureEvents();
		if (postures != null && postures.size() > 0) {
			System.out.print(", Posture Status=" + postures.get(0).getStatus());
			
			Calendar cal  = postures.get(0).getLastUpdateTime();
			System.out.print(", Posture Timestamp=" + ((cal != null) ? cal.getTime(): ""));
			
		}
		System.out.print(", Session Last Update Time=" + session.getLastUpdateTime().getTime());
		//Get Generic Attributes
		List<GenericAttribute> attributes= session.getExtraAttributes();
		for(GenericAttribute attrib: attributes) {
			
			System.out.print(", Session attributeName=" + attrib.getName());
			if(attrib.getType()==GenericAttributeValueType.STRING) {
				String attribValue = null;
				try {
					attribValue = new String(attrib.getValue(),"UTF-8");
				} catch (UnsupportedEncodingException e) {
					
					e.printStackTrace();
				}
				System.out.print(", Session attributeValue=" + attribValue);
			}
		}
		System.out.println("}");
	}

	public static void print(SXPBinding binding) {
		StringBuilder sb = new StringBuilder("SXPBinding={");
		sb.append("ipPrefix=" + binding.getIpPrefix());
		sb.append(" tag=" + binding.getTag());
		sb.append(" source=" + binding.getSource());
		sb.append(" peerSequence=" + binding.getPeerSequence());
		sb.append("}");
		System.out.println(sb.toString());
	}
	
	private class MyListener implements Listener {

		@Override
		public void beforeConnect() {
			System.out.println("Connecting...");
		}

		@Override
		public void onConnected() {
			System.out.println("Connected");
			synchronized (SampleHelper.this) {
				connected = true;
				SampleHelper.this.notify();
			}
		}

		@Override
		public void onDisconnected() {
			if (connected) {
				System.out.println("Connection closed");
				connected = false;
			}
		}

		@Override
		public void onDeleted() {
			System.out.println("Account deleted");
		}

		@Override
		public void onDisabled() {
			System.out.println("Account disabled");
		}

		@Override
		public void onEnabled() {
			System.out.println("Account enabled");
		}

		@Override
		public void onAuthorizationChanged() {
			System.out.println("Authorization changed");
		}
	}

}
