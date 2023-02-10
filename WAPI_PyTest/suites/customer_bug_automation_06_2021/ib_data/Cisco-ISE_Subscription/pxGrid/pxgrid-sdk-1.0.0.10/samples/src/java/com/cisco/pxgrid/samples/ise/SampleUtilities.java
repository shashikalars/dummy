package com.cisco.pxgrid.samples.ise;

import java.io.FileInputStream;
import java.security.KeyStore;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.List;

import com.cisco.pxgrid.model.core.IPInterfaceIdentifier;
import com.cisco.pxgrid.model.net.DevicePortIdentifier;
import com.cisco.pxgrid.model.net.Port;
import com.cisco.pxgrid.model.net.PostureAssessment;
import com.cisco.pxgrid.model.net.RADIUSAVPair;
import com.cisco.pxgrid.model.net.Session;
import com.cisco.pxgrid.model.net.User;

/**
 * A class containing helpful methods used by the pxGrid samples.
 * 
 * @author jangwin
 *
 */

public class SampleUtilities {
	private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy.MM.dd HH:mm:ss");

	/**
	 * Determines if a keystore file and password is valid.
	 * 
	 * @param filename the keystore file in JKS format
	 * @param password password for the keystore file
	 * @return
	 */

	public static boolean isValid(String filename, String password)
	{
		try {
			KeyStore ks = KeyStore.getInstance("JKS");
			ks.load(new FileInputStream(filename), password.toCharArray());

			return true;
		} catch (Exception e) {
			return false;
		}
	}
	
	public static void print(Session session) {
		System.out.print("\nsession (ip=" +
				session.getInterface().getIpIntfIDs().get(0).getIpAddress());

		System.out.print(", Audit Session Id=" +session.getGid());
		User user = session.getUser();
		if (user != null) {
			System.out.print(", User Name=" + user.getName());
			System.out.print(", AD User DNS Domain=" + user.getADUserDNSDomain());
			System.out.print(", AD Host DNS Domain=" + user.getADHostDNSDomain());
			System.out.print(", AD User NetBIOS Name=" + user.getADUserNetBIOSName());
			System.out.print(", AD Host NETBIOS Name=" + user.getADHostNetBIOSName());
		}

		//Mac address
		List<String> macs = session.getInterface().getMacAddresses();
		if (macs != null && macs.size() > 0) {
			System.out.print(", Calling station id=" + macs.get(0));
		}

		//Session State 
		System.out.print(", Session state= " + session.getState());			

		System.out.print(", Epsstatus=" + session.getEPSStatus());

		//Security group
		System.out.print(", Security Group=" +  session.getSecurityGroup());

		//Endpoint profile
		System.out.print(", Endpoint Profile=" +  session.getEndpointProfile());

		//Port and NAS Ip information
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
		
		//RADIUS AV pair
		List<RADIUSAVPair> radiusAVPairs = session.getRADIUSAttrs();
		if (radiusAVPairs != null && !radiusAVPairs.isEmpty()) {
			System.out.print(", RADIUSAVPairs=[");
			for(RADIUSAVPair p : radiusAVPairs) {
				System.out.print(" " + p.getAttrName() + "=" + p.getAttrValue() );
			}
			System.out.print("]");
		}
		
		//Posture Info
		List<PostureAssessment> postures = session.getAssessedPostureEvents();
		if (postures != null && postures.size() > 0) {
			System.out.print(", Posture Status=" + postures.get(0).getStatus());
			
			Calendar cal  = postures.get(0).getLastUpdateTime();
			System.out.print(", Posture Timestamp=" + ((cal != null) ? cal.getTime(): ""));
			
		}
		System.out.print(", Session Last Update Time=" + session.getLastUpdateTime().getTime() + " )");
	}

	public static String hostnamesToString(String[] hostnames) {
		String hostnamesStr = null;
		for (String hostname : hostnames) {
			if (hostnamesStr == null) {
				hostnamesStr = hostname;
			} else {
				hostnamesStr += ", ";
				hostnamesStr += hostname;
			}
		}

		return hostnamesStr;
	}

	public static String timeToString(Calendar time) {
		if (time == null) {
			return "null";
		} else {
			return DATE_FORMAT.format(time.getTime());
		}
	}

	public static Calendar parseTime(String timeStr)
		throws ParseException
	{
		if (timeStr != null) {
			Calendar start = Calendar.getInstance();
			start.setTime(DATE_FORMAT.parse(timeStr));

			return start;
		} else {
			return null;
		}
	}
}
