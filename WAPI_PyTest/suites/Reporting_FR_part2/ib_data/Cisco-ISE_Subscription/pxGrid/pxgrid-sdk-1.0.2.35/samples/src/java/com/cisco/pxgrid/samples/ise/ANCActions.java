package com.cisco.pxgrid.samples.ise;

import java.util.List;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.anc.ANCClient;
import com.cisco.pxgrid.anc.ANCQuery;
import com.cisco.pxgrid.model.anc.ANCAction;
import com.cisco.pxgrid.model.anc.ANCPolicy;
import com.cisco.pxgrid.model.anc.ANCResult;

public class ANCActions {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		ANCClient client = new ANCClient();
		ANCQuery query = client.createANCQuery(grid);

		String policyName, mac, ip;
		ANCResult result = null;
		ANCPolicy ancPolicy;
		String actionVal;
		List<ANCAction> actionList;
		
		operationLoop:
		while (true) {
			System.out.println("Operation selection:");
			System.out.println("  1. ApplyEndpointPolicyByMAC");
			System.out.println("  2. ClearEndpointPolicyByMAC");
			System.out.println("  3. ApplyEndpointPolicyByIP");
			System.out.println("  4. ClearEndpointPolicyByIP");
			System.out.println("  5. GetEndpointByIP");
			System.out.println("  6. Subscribe");
			System.out.println("  7. CreatePolicy");
			System.out.println("  8. UpdatePolicy");
			System.out.println("  9. DeletePolicy");
			System.out.println("  10. GetPolicyByName");
			System.out.println("  11. GetAllPolicies");
			System.out.println("  12. GetEndPointByMAC");
			System.out.println("  13. GetAllEndpoints");
			System.out.println("  14. GetEndpointByPolicy");
			
			String value = helper.prompt("Enter number (or <enter> to disconnect): ");
			if (value == null) break;
			int operation;
			try {
			 operation = Integer.parseInt(value);
			}
			catch(NumberFormatException ex)
			{
				continue;
			}
			switch (operation) {
			case 1:
				policyName = helper.prompt("Policy name (or <enter> to disconnect): ");
				if (policyName == null) break operationLoop;
				mac = helper.prompt("MAC address (or <enter> to disconnect): ");
				if (mac == null) break operationLoop;
				result = query.applyEndpointPolicyByMAC(policyName, mac);
				break;
			case 2:
				mac = helper.prompt("MAC address (or <enter> to disconnect): ");
				if (mac == null) break operationLoop;
				result = query.clearEndpointPolicyByMAC(mac);
				break;
			case 3:
				policyName = helper.prompt("Policy name (or <enter> to disconnect): ");
				if (policyName == null) break operationLoop;
				ip = helper.prompt("IP address (or <enter> to disconnect): ");
				if (ip == null) break operationLoop;
				result = query.applyEndpointPolicyByIP(policyName, ip);
				break;
			case 4:
				ip = helper.prompt("IP address (or <enter> to disconnect): ");
				if (ip == null) break operationLoop;
				result = query.clearEndpointPolicyByIP(ip);
				break;
			case 5:
				ip = helper.prompt("IP address (or <enter> to disconnect): ");
				if (ip == null) break operationLoop;
				result = query.getEndpointByIP(ip);
				break;
			case 6:
				query.registerNotification(grid, new ANCNotificationHandlers.ApplyEndpointPolicyNotificationHandler());
				query.registerNotification(grid, new ANCNotificationHandlers.ClearEndpointPolicyNotificationHandler());
				query.registerNotification(grid, new ANCNotificationHandlers.CreatePolicyNotificationHandler());
				query.registerNotification(grid, new ANCNotificationHandlers.UpdatePolicyNotificationHandler());
				query.registerNotification(grid, new ANCNotificationHandlers.DeletePolicyNotificationHandler());
				helper.prompt("Press <enter> to disconnect: ");
				break operationLoop;
			case 7: //Create policy
				ancPolicy= new ANCPolicy();
				policyName = helper.prompt("Policy name (or <enter> to disconnect): ");
				if (policyName == null) break operationLoop;
				ancPolicy.setName(policyName);
				actionList = ancPolicy.getActions();
				int count;
				int actionValInt;
				actionLoop:
				while(true){
					System.out.println("ANC Actions:");
					count = 1;
					for (ANCAction c: ANCAction.values()) {
						System.out.println(count++ + ". " + c.name());
			        }
					System.out.println("0. End adding actions");
					actionVal = helper.prompt("Enter ANC action (or <enter> to disconnect): ");
					if (actionVal == null) break;
					actionValInt = Integer.parseInt(actionVal);
					ANCAction ancAction;
					switch(actionValInt){
					case 1: ancAction = ANCAction.QUARANTINE; break;
					case 2: ancAction = ANCAction.REMEDIATE; break;
					case 3: ancAction = ANCAction.PROVISIONING; break;
					case 4: ancAction = ANCAction.SHUT_DOWN; break;
					case 5: ancAction = ANCAction.PORT_BOUNCE; break;
					case 0:break actionLoop;
					default: System.out.println("Please enter the valid option");
					         continue;
					}
					actionList.add(ancAction);
				}
				result = query.createPolicy(ancPolicy);
				break;
			case 8: //update policy
				ancPolicy= new ANCPolicy();
				policyName = helper.prompt("Policy name (or <enter> to disconnect): ");
				if (policyName == null) break operationLoop;
				ancPolicy.setName(policyName);
				actionList = ancPolicy.getActions();
				actionLoop:
				while(true){
					System.out.println("ANC Actions:");
					count = 1;
					for (ANCAction c: ANCAction.values()) {
						System.out.println(count++ + ". " + c.name());
			        }
					System.out.println("0. End adding actions");
					actionVal = helper.prompt("Enter ANC action (or <enter> to disconnect): ");
					if (actionVal == null) break;
					actionValInt = Integer.parseInt(actionVal);
					ANCAction ancAction;
					switch(actionValInt){
					
					case 1: ancAction = ANCAction.QUARANTINE; break;
					case 2: ancAction = ANCAction.REMEDIATE; break;
					case 3: ancAction = ANCAction.PROVISIONING; break;
					case 4: ancAction = ANCAction.SHUT_DOWN; break;
					case 5: ancAction = ANCAction.PORT_BOUNCE; break;
					case 0:break actionLoop;
					default: System.out.println("Please enter the valid option");
					         continue;
					}
					actionList.add(ancAction);
				}
				result = query.updatePolicy(ancPolicy);
				break;	
			case 9: //delete policy	
				policyName = helper.prompt("Policy name (or <enter> to disconnect): ");
				if (policyName == null) break operationLoop;
				result = query.deletePolicy(policyName);
				break;
			case 10: //get policy by name
				policyName = helper.prompt("Policy name (or <enter> to disconnect): ");
				if (policyName == null) break operationLoop;
				result = query.retrievePolicyByName(policyName);
				break;
			case 11: //retrieve all policies
				result = query.retrieveAllPolicies();
				break;
			case 12: //get endpoint by MAC
				mac = helper.prompt("Enter MAC address (or <enter> to disconnect): ");
				if (mac == null) break operationLoop;
				result = query.getEndpointByMAC(mac);
				break;	
			case 13: //get all endpoints
				result = query.getAllEndpoints();
				break;	
			case 14: //get endpointByPolicy
				policyName = helper.prompt("Policy name (or <enter> to disconnect): ");
				if (policyName == null) break operationLoop;
				result = query.retrieveEndpointByPolicy(policyName);
				break;		
			default:
				System.out.println("Unknown selection");
				break operationLoop;
			}
			System.out.println("ANCResult=" + result);
		}
		helper.disconnect();
	}
}
