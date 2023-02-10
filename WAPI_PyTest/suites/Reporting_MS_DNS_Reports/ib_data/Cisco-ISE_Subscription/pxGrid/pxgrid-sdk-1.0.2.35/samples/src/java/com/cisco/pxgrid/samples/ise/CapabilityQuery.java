package com.cisco.pxgrid.samples.ise;

import com.cisco.pxgrid.GCLException;
import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.internal.Grid;
import com.cisco.pxgrid.model.core.Capability;
import com.cisco.pxgrid.model.core.GetCapabilityListRequest;
import com.cisco.pxgrid.model.core.GetCapabilityListResponse;

/**
 * Demonstrates how to use a pxGrid client to query controller for all capabilities.
 */
public class CapabilityQuery {
	public static void main(String[] args) throws Exception {
		SampleHelper helper = new SampleHelper();
		GridConnection grid = helper.connectWithReconnectionManager();

		GetCapabilityListRequest req = new GetCapabilityListRequest();
		GetCapabilityListResponse resp = (GetCapabilityListResponse)grid.query(req, Grid.CONTROLLER_JID);
		if (resp.getError() != null) {
			throw new GCLException(resp.getError().getDescription());
		}
		for (Capability cap : resp.getCapabilities()) {
			System.out.println("capability=" + cap.getName() + ", version=" + cap.getVersion());
		}
		helper.disconnect();
	}
}
