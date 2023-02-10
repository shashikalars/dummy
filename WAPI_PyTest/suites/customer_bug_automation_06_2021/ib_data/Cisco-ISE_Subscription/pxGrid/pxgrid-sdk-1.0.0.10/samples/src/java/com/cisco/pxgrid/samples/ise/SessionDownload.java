package com.cisco.pxgrid.samples.ise;

import java.util.Calendar;
import java.util.Date;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.cisco.pxgrid.GridConnection;
import com.cisco.pxgrid.ReconnectionManager;
import com.cisco.pxgrid.TLSConfiguration;
import com.cisco.pxgrid.model.core.SubnetContentFilter;
import com.cisco.pxgrid.model.ise.Group;
import com.cisco.pxgrid.model.net.Session;
import com.cisco.pxgrid.stub.identity.SessionDirectoryFactory;
import com.cisco.pxgrid.stub.identity.SessionDirectoryQuery;
import com.cisco.pxgrid.stub.identity.SessionIterator;

/**
 * Demonstrates how to use an xGrid client to download all active sessions from
 * ISE.
 * 
 * @author jangwin
 *
 */

public class SessionDownload {
	protected static final Logger log = LoggerFactory.getLogger(SessionDownload.class);

	public static void main(String [] args)
		throws Exception
	{
		// collect command line parameters using helper class. custom implementations
		// will likely gather this information from a source other than command line.

		SampleProperties props = SampleProperties.load();
		SampleParameters params = new SampleParameters(props);
		params.appendCommonOptions();
		params.appendFilterOption();
		params.appendStartOption();
		params.appendEndOption();

		CommandLine line = null;
		try {
			line = params.process(args);
		} catch (IllegalArgumentException e) {
			System.err.println("illegal argument: " + e.getMessage() + "\n");

			params.printHelp("session_download");
			System.exit(1);
		} catch (ParseException e) {
			params.printHelp("session_download");
			System.exit(1);
		}


		String[] hostnames = params.retrieveHostnames(line);
		String username = params.retrieveUsername(line);
		String keystoreFilename = params.retrieveKeystoreFilename(line);
		String keystorePassword = params.retrieveKeystorePassword(line);
		String truststoreFilename = params.retrieveTruststoreFilename(line);
		String truststorePassword = params.retrieveTruststorePassword(line);
		SubnetContentFilter filter = params.retrieveFilter(line);
		String filterStr = params.retrieveFilterStr(line);
		Calendar start = params.retrieveStart(line);
		Calendar end = params.retrieveEnd(line);

		System.out.println("------- properties -------");
		System.out.println("version=" + props.getVersion());
		System.out.println("hostnames=" + SampleUtilities.hostnamesToString(hostnames));
		System.out.println("username=" + username);
		System.out.println("keystoreFilename=" + keystoreFilename);
		System.out.println("keystorePassword=" + keystorePassword);
		System.out.println("truststoreFilename=" + truststoreFilename);
		System.out.println("truststorePassword=" + truststorePassword);
		System.out.println("filter=" + filterStr);
		System.out.println("start=" + SampleUtilities.timeToString(start));
		System.out.println("end=" + SampleUtilities.timeToString(end));
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


		SessionDirectoryQuery sd = SessionDirectoryFactory.createSessionDirectoryQuery(con);
		SessionIterator iterator = sd.getSessionsByTime(start, end, filter);
		iterator.open();

		Date startedAt = new Date();
		System.out.println("starting at " + startedAt.toString() + "...");

		int count = 0;
		Session s = iterator.next();
		while (s != null) {
			// when testing performance, comment out the following line. otherwise
			// excessive console IO will adversely affect results
			SampleUtilities.print(s);

			s = iterator.next();
			count++;

			if (count % 1000 == 0) {
				System.out.println("count: " + count);
			}
		}

		Date endedAt = new Date();
		System.out.println("... ending at: " + endedAt.toString());

		System.out.println("\n---------------------------------------------------");
		System.out.println("downloaded " + count + " sessions in " + (endedAt.getTime() - startedAt.getTime()) + " milliseconds");
		System.out.println("---------------------------------------------------\n");

		iterator.close();


		// disconnect from xGrid. with reconnection manager enabled we only need to call stop.

		recon.stop();
	}
}
