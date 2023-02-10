package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.anc.ApplyEndpointPolicyNotifHandler;
import com.cisco.pxgrid.anc.ClearEndpointPolicyNotifHandler;
import com.cisco.pxgrid.anc.CreatePolicyNotifHandler;
import com.cisco.pxgrid.anc.UpdatePolicyNotifHandler;
import com.cisco.pxgrid.anc.DeletePolicyNotifHandler;
import com.cisco.pxgrid.model.anc.ANCAction;
import com.cisco.pxgrid.model.anc.ANCEndpoint;
import com.cisco.pxgrid.model.anc.ANCPolicy;

/**
 * This class holds all ANC Notification Handlers
 * for subscribe 
 * 
 */
public class ANCNotificationHandlers {
	private static String printANCEndpoint(ANCEndpoint endpoint) {
		StringBuffer buffer = new StringBuffer();
		if(endpoint != null) {
			String mac;
			if((mac = endpoint.getMacAddress()) != null) {
				buffer.append("MAC Address=" + mac + " ");
			}
			String policy;
			if((policy = endpoint.getPolicyName()) != null) {
				buffer.append("Policy=" + policy + " ");
			}
			String ip;
			if((ip = endpoint.getIpAddress()) != null) {
				buffer.append(" IP Address=" + ip);	
			}
		}
		return buffer.toString();	
	}
	
	private static String printANCPolicy(ANCPolicy policy) {
		StringBuffer buffer = new StringBuffer();
		if (policy != null) {
			buffer.append("Policy=" + policy.getName() + " ");
			buffer.append("Action(s)=");
			for (ANCAction action : policy.getActions()) {
				buffer.append(action.name() + " ");
			}

		}
		return buffer.toString();
	}
	
	public static class ApplyEndpointPolicyNotificationHandler
	implements ApplyEndpointPolicyNotifHandler {

		@Override
		public void onChange(ANCEndpoint endpoint) {
			System.out.println("\nApply Endpoint Policy Notification:");
			System.out.println(printANCEndpoint(endpoint));
		}
	}
	
	public static class ClearEndpointPolicyNotificationHandler
	implements ClearEndpointPolicyNotifHandler {

		@Override
		public void onChange(ANCEndpoint endpoint) {
			System.out.println("\nClear Endpoint Policy Notification:");
			System.out.println(printANCEndpoint(endpoint));
		}
	}
	
	public static class CreatePolicyNotificationHandler
	implements CreatePolicyNotifHandler {

		@Override
		public void onChange(ANCPolicy policy) {
			System.out.println("\nCreatePolicyNotification:");
			System.out.println(printANCPolicy(policy));
		}
	}
	
	public static class UpdatePolicyNotificationHandler
	implements UpdatePolicyNotifHandler {

		@Override
		public void onChange(ANCPolicy oldPolicy, ANCPolicy newPolicy) {
			System.out.println("\nUpdatePolicyNotification:");
			System.out.println("Old policy: ");
			System.out.println(printANCPolicy(oldPolicy));
			System.out.println("New policy: ");
			System.out.println(printANCPolicy(newPolicy));
		}
	}
	
	public static class DeletePolicyNotificationHandler
	implements DeletePolicyNotifHandler {

		@Override
		public void onChange(ANCPolicy policy) {
			System.out.println("\nDeletePolicyNotification:");
			System.out.println(printANCPolicy(policy));
		}
	}
}
