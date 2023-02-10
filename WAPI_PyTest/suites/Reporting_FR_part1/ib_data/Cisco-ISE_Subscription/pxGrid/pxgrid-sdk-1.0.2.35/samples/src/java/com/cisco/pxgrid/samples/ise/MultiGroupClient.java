package com.cisco.pxgrid.samples.ise;

import java.net.InetAddress;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.anc.ANCClient;
import com.cisco.pxgrid.anc.ANCQuery;
import com.cisco.pxgrid.model.anc.ANCAction;
import com.cisco.pxgrid.model.anc.ANCPolicy;
import com.cisco.pxgrid.model.anc.ANCResult;
import com.cisco.pxgrid.model.net.Session;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;
import com.cisco.pxgrid.stub.identity.SessionDirectoryQuery;

/**
 * Sample to demonstrate a client is able to perform actions on multiple topics 
 * Creates ANC policy which requires client to have ANC group auth
 * Queries Session Directory for a given IP which requires Session group auth 
 * Client should have both ANC and Session group membership
 */

public class MultiGroupClient {
	public static final String DEF_POLICY_NAME = "ANC"+System.currentTimeMillis();
	public static final String DEF_SESSION_IP = "1.1.1.2";
	public static final ANCAction DEF_ANC_POLICY_ACTION = ANCAction.PORT_BOUNCE;
	public static final String POLICY_NAME_PROP = "POLICY_NAME";
	public static final String SESSION_IP_PROP = "SESSION_IP";
	
	public static void main(String[] args) throws Exception {
	SampleHelper helper = new SampleHelper();
	GridConnection grid = helper.connectWithReconnectionManager();
	 
	String policy = System.getProperty(POLICY_NAME_PROP);
	String sessionip = System.getProperty(SESSION_IP_PROP);
	
	//create ANC policy
	//if ANC policy name is not provided, a random policy name will be generated
	ANCClient client = new ANCClient();
	ANCQuery query = client.createANCQuery(grid);
	ANCPolicy ancPolicy= new ANCPolicy();
	ancPolicy.setName(policy!=null && !policy.isEmpty() ? policy:DEF_POLICY_NAME);
	ancPolicy.getActions().add(DEF_ANC_POLICY_ACTION);
	ANCResult ancResult = query.createPolicy(ancPolicy);
	
	System.out.println("Create ANC Policy: " + ancPolicy.getName() + " Result - " + ancResult);
	
	//query session directory for an IP
	//if IP is not provided, 1.1.1.2 will be used as default
	
	SessionDirectoryQuery sessionquery = SessionDirectoryFactory
			.createSessionDirectoryQuery(grid);

	sessionip = sessionip!=null && !sessionip.isEmpty() ? sessionip : DEF_SESSION_IP;
	Session session = sessionquery.getActiveSessionByIPAddress(InetAddress
			.getByName(sessionip));
	if (session != null) {
		SampleHelper.print(session);
	} else {
		System.out.println("Session " + sessionip + " not found");
	}
				
	helper.disconnect();
	}
}
