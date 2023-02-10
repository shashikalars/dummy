package com.cisco.pxgrid.samples.ise;

import java.util.Scanner;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.cisco.pxgrid.GCLException;
import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.ReconnectionManager;
import com.cisco.pxgrid.TLSConfiguration;
import com.cisco.pxgrid.model.ise.Group;
import com.cisco.pxgrid.stub.eps.EPSClientStub;
import com.cisco.pxgrid.stub.eps.EPSQuery;

/**
 * Demonstrates how to use a pxGrid client to invoke an Endpoint Protection
 * Service (EPS) quarantine by IP address in ISE.
 * 
 * @author jangwin
 *
 */

public class EPSQuarantine {
	protected static final Logger log = LoggerFactory.getLogger(EPSQuarantine.class);

	public static void main(String[] args)
		throws Exception
	{
		// collect command line parameters using helper class. custom implementations
		// will likely gather this information from a source other than command line.

		SampleProperties props = SampleProperties.load();
		SampleParameters params = new SampleParameters(props);
		params.appendCommonOptions();

		CommandLine line = null;
		try {
			line = params.process(args);
		} catch (IllegalArgumentException e) {
			params.printHelp("eps_quarantine");
			System.exit(1);
		} catch (ParseException e) {
			params.printHelp("eps_quarantine");
			System.exit(1);
		}

		String[] hostnames = params.retrieveHostnames(line);
		String username = params.retrieveUsername(line);
		String keystoreFilename = params.retrieveKeystoreFilename(line);
		String keystorePassword = params.retrieveKeystorePassword(line);
		String truststoreFilename = params.retrieveTruststoreFilename(line);
		String truststorePassword = params.retrieveTruststorePassword(line);

		System.out.println("------- properties -------");
		System.out.println("version=" + props.getVersion());
		System.out.println("hostnames=" + SampleUtilities.hostnamesToString(hostnames));
		System.out.println("username=" + username);
		System.out.println("keystoreFilename=" + keystoreFilename);
		System.out.println("keystorePassword=" + keystorePassword);
		System.out.println("truststoreFilename=" + truststoreFilename);
		System.out.println("truststorePassword=" + truststorePassword);
		System.out.println("--------------------------");


		// check keystore

		if (!SampleUtilities.isValid(keystoreFilename, keystorePassword)) {
			System.err.println("unable to read keystore. please check the keystore filename and keystore password.");
			System.exit(1);
		}


		// check truststore

		if (!SampleUtilities.isValid(truststoreFilename, truststorePassword)) {
			System.err.println("unable to read truststore. please check the truststore filename and truststore password.");
			System.exit(1);
		}


		// assemble configuration

		TLSConfiguration config = new TLSConfiguration();
		config.setHosts(hostnames);
		config.setUserName(username);
		config.setGroup(Group.EPS.value());
		config.setKeystorePath(keystoreFilename);
		config.setKeystorePassphrase(keystorePassword);
		config.setTruststorePath(truststoreFilename);
		config.setTruststorePassphrase(truststorePassword);


		// initialize pxGrid connection

		GridConnection con = new GridConnection(config);
		con.addListener(new SampleConnectionListener());


		// use reconnection manager to ensure connection gets re-established
		// if dropped. this technique is recommended.

		ReconnectionManager recon = new ReconnectionManager(con);
		recon.setRetryMillisecond(2000);
		recon.start();

		while (!con.isConnected()) {
			Thread.sleep(100);
		}


		// create query we'll use to make call

		EPSClientStub stub = new EPSClientStub();
		EPSQuery query = stub.createEPSQuery(con);


		// quarantine ip addresses based on user input

		Scanner scanner = new Scanner(System.in);
		while (true) {
			System.out.print("ip address (or <enter> to disconnect): ");
			String ip = scanner.nextLine();

			if (ip == null || "".equals(ip)) {
				break;
			}

			try {
				query.quarantineByIP(ip);
			} catch (GCLException e) {
				System.out.println("GCLException msg=" + e.getMessage());
			}
		}
		scanner.close();


		// disconnect from pxGrid. with reconnection manager enabled we only need to call stop.

		recon.stop();
	}
}
