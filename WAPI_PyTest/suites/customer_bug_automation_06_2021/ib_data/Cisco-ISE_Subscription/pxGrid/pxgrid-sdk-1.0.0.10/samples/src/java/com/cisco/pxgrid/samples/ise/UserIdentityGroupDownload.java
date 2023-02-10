package com.cisco.pxgrid.samples.ise;

import java.util.Date;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.ReconnectionManager;
import com.cisco.pxgrid.TLSConfiguration;
import com.cisco.pxgrid.model.ise.Group;
import com.cisco.pxgrid.model.net.User;
import com.cisco.pxgrid.stub.identity.IdentityGroupQuery;
import com.cisco.pxgrid.stub.identity.Iterator;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;

/**
 * Demonstrates how to use an xGrid client to download all identity groups in
 * ISE.
 * 
 * @author jangwin
 *
 */

public class UserIdentityGroupDownload {
	protected static final Logger log = LoggerFactory.getLogger(UserIdentityGroupDownload.class);

	public static void main(String [] args)
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
			params.printHelp("identity_group_download");
			System.exit(1);
		} catch (ParseException e) {
			params.printHelp("identity_group_download");
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
		config.setGroup(Group.SESSION.value());
		config.setKeystorePath(keystoreFilename);
		config.setKeystorePassphrase(keystorePassword);
		config.setTruststorePath(truststoreFilename);
		config.setTruststorePassphrase(truststorePassword);


		// initialize xgrid connection

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


		// construct a date range of requested sessions

		IdentityGroupQuery sd = SessionDirectoryFactory.createIdentityGroupQuery(con);
		Iterator<User> iterator = sd.getIdentityGroups();
		iterator.open();

		Date startedAt = new Date();
		System.out.println("starting at " + startedAt.toString() + "...");

		int count = 0;
		User s = iterator.next();
		while (s != null) {
			// when testing performance, comment out the following line. otherwise
			// excessive console IO will adversely affect results
			System.out.println("user=" + s.getName() + " groups=" + s.getGroupList().getObjects().get(0).getName());
			s = iterator.next();
			count++;

			if (count % 1000 == 0) {
				System.out.println("count: " + count);
			}
		}

		Date endedAt = new Date();
		System.out.println("... ending at: " + endedAt.toString());

		System.out.println("\n---------------------------------------------------");
		System.out.println("downloaded " + count + " users in " + (endedAt.getTime() - startedAt.getTime()) + " milliseconds");
		System.out.println("---------------------------------------------------\n");

		iterator.close();


		// disconnect from xGrid. with reconnection manager enabled we only need to call stop.

		recon.stop();
	}
}
