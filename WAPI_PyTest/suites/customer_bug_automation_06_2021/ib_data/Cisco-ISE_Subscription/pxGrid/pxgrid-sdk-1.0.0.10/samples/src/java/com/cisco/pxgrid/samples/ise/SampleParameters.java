package com.cisco.pxgrid.samples.ise;

import java.util.Calendar;
import java.util.regex.Pattern;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.cisco.pxgrid.model.core.Subnet;
import com.cisco.pxgrid.model.core.SubnetContentFilter;
import com.cisco.pxgrid.model.ise.Group;

/**
 * A class to manage the collection of command line parameters for the samples.
 * Customer implementations using pxGrid clients will likely gather this
 * information from other sources. So this class is only useful to manage
 * parameters in the context of the samples.
 * 
 * @author jangwin
 *
 */

public class SampleParameters {
	private SampleProperties properties;
	private Option hostnameOpt;
	private Option usernameOpt;
	private Option descriptionOpt;
	private Option keystoreFilenameOpt;
	private Option keystorePasswordOpt;
	private Option truststoreFilenameOpt;
	private Option truststorePasswordOpt;
	private Option groupOpt;
	private Option filterOpt;
	private Option startOpt;
	private Option endOpt;
	private Options options;

	public SampleParameters(SampleProperties properties) {
		this.properties = properties;
	}

	/**
	 * Adds command line options common to all pxGrid samples.
	 */

	public void appendCommonOptions() {
		if (this.properties.getHostnames() == null) {
			this.hostnameOpt = new Option(SampleProperties.PROPERTY_HOSTNAME, true, "hostname of pxgrid (required)");
			this.hostnameOpt.setArgName("hostname");
			this.hostnameOpt.setRequired(true);
			this.hostnameOpt.setArgs(Integer.MAX_VALUE);
		} else {
			this.hostnameOpt = new Option(SampleProperties.PROPERTY_HOSTNAME, true, "hostname of pxgrid (optional, default=" + this.properties.getHostnames() + ")");
			this.hostnameOpt.setArgName("hostname");
			this.hostnameOpt.setRequired(false);
			this.hostnameOpt.setArgs(Integer.MAX_VALUE);
		}

		if (this.properties.getUsername() == null) {
			this.usernameOpt = new Option(SampleProperties.PROPERTY_USERNAME, true, "username of pxgrid client (required)");
			this.usernameOpt.setArgName("username");
			this.usernameOpt.setRequired(true);
		} else {
			this.usernameOpt = new Option(SampleProperties.PROPERTY_USERNAME, true, "username of pxgrid client (optional, default=" + this.properties.getUsername() + ")");
			this.usernameOpt.setArgName("username");
			this.usernameOpt.setRequired(false);
		}

		if (this.properties.getKeystoreFilename() == null) {
			this.keystoreFilenameOpt = new Option(SampleProperties.PROPERTY_KEYSTORE_FILENAME, true, "keystore to use for connection (required)");
			this.keystoreFilenameOpt.setArgName("filename");
			this.keystoreFilenameOpt.setRequired(true);
		} else {
			this.keystoreFilenameOpt = new Option(SampleProperties.PROPERTY_KEYSTORE_FILENAME, true, "keystore to use for connection (optional, default=" + this.properties.getKeystoreFilename() + ")");
			this.keystoreFilenameOpt.setArgName("filename");
			this.keystoreFilenameOpt.setRequired(false);
		}

		if (this.properties.getKeystorePassword() == null) {
			this.keystorePasswordOpt = new Option(SampleProperties.PROPERTY_KEYSTORE_PASSWORD, true, "password for keystore (required)");
			this.keystorePasswordOpt.setArgName("password");
			this.keystorePasswordOpt.setRequired(true);
		} else {
			this.keystorePasswordOpt = new Option(SampleProperties.PROPERTY_KEYSTORE_PASSWORD, true, "password for keystore (optional, default=" + this.properties.getKeystorePassword() + ")");
			this.keystorePasswordOpt.setArgName("password");
			this.keystorePasswordOpt.setRequired(false);
		}

		if (this.properties.getTruststoreFilename() == null) {
			this.truststoreFilenameOpt = new Option(SampleProperties.PROPERTY_TRUSTSTORE_FILENAME, true, "truststore to use for connection (required)");
			this.truststoreFilenameOpt.setArgName("filename");
			this.truststoreFilenameOpt.setRequired(true);
		} else {
			this.truststoreFilenameOpt = new Option(SampleProperties.PROPERTY_TRUSTSTORE_FILENAME, true, "truststore to use for connection (optional, default=" + this.properties.getTruststoreFilename() + ")");
			this.truststoreFilenameOpt.setArgName("filename");
			this.truststoreFilenameOpt.setRequired(false);
		}

		if (this.properties.getTruststorePassword() == null) {
			this.truststorePasswordOpt = new Option(SampleProperties.PROPERTY_TRUSTSTORE_PASSWORD, true, "password for truststore (required)");
			this.truststorePasswordOpt.setArgName("password");
			this.truststorePasswordOpt.setRequired(true);
		} else {
			this.truststorePasswordOpt = new Option(SampleProperties.PROPERTY_TRUSTSTORE_PASSWORD, true, "password for truststore (optional, default=" + this.properties.getTruststorePassword() + ")");
			this.truststorePasswordOpt.setArgName("password");
			this.truststorePasswordOpt.setRequired(false);
		}

		this.options = new Options();
		this.options.addOption(this.hostnameOpt);
		this.options.addOption(this.usernameOpt);
		this.options.addOption(this.keystoreFilenameOpt);
		this.options.addOption(this.keystorePasswordOpt);
		this.options.addOption(this.truststoreFilenameOpt);
		this.options.addOption(this.truststorePasswordOpt);
	}

	/**
	 * Adds a message filtering option to the command line options.
	 */

	public void appendFilterOption() {
		if (this.properties.getFilter() == null) {
			this.filterOpt = new Option(SampleProperties.PROPERTY_FILTER, true, "subnet filter (optional)");
			this.filterOpt.setArgs(Integer.MAX_VALUE);
			this.filterOpt.setArgName("<network ip>:<netmask>");
			this.filterOpt.setRequired(false);
		} else {
			this.filterOpt = new Option(SampleProperties.PROPERTY_FILTER, true, "subnet filter (optional, default=" + this.properties.getFilter() + ")");
			this.filterOpt.setArgs(Integer.MAX_VALUE);
			this.filterOpt.setArgName("<network ip>:<netmask>");
			this.filterOpt.setRequired(false);
		}

		this.options.addOption(this.filterOpt);
	}

	/**
	 * Adds a pxGrid description option to the command line options.
	 */

	public void appendDescriptionOption() {
		if (this.properties.getDescription() == null) {
			this.descriptionOpt = new Option(SampleProperties.PROPERTY_DESCRIPTION, true, "description for pxgrid client (optional)");
			this.descriptionOpt.setArgName("description");
			this.descriptionOpt.setRequired(false);
		} else {
			this.descriptionOpt = new Option(SampleProperties.PROPERTY_DESCRIPTION, true, "description for pxgrid client (optional, default=" + this.properties.getDescription() + ")");
			this.descriptionOpt.setArgName("description");
			this.descriptionOpt.setRequired(false);
		}

		this.options.addOption(this.descriptionOpt);
	}

	/**
	 * Adds a group option to the command line options.
	 */

	public void appendGroupOption() {
		if (this.properties.getGroup() == null) {
			this.groupOpt = new Option(SampleProperties.PROPERTY_GROUP, true, "desired group (case sensitive, required)");
			this.groupOpt.setArgName("Basic|Administrator|Session|EPS");
			this.groupOpt.setRequired(true);
		} else {
			this.groupOpt = new Option(SampleProperties.PROPERTY_GROUP, true, "desired group (optional, default=" + this.properties.getGroup() + ")");
			this.groupOpt.setArgName("Basic|Administrator|Session|EPS");
			this.groupOpt.setRequired(false);
		}

		this.options.addOption(this.groupOpt);
	}

	/**
	 * Adds a start option to the command line options.
	 */

	public void appendStartOption() {
		this.startOpt = new Option(SampleProperties.PROPERTY_START, true, "start date (ex. '2014.09.04 13:00:00', optional)");
		this.startOpt.setArgName("date");
		this.startOpt.setRequired(false);

		this.options.addOption(this.startOpt);
	}

	/**
	 * Adds an end option to the command line options.
	 */

	public void appendEndOption() {
		this.endOpt = new Option(SampleProperties.PROPERTY_END, true, "end date (ex. '2014.09.04 14:00:00', optional)");
		this.endOpt.setArgName("date");
		this.endOpt.setRequired(false);

		this.options.addOption(this.endOpt);
	}

	/**
	 * Parses an array of string arguments presented by the user into more
	 * structured arguments that can be read by the samples.
	 * 
	 * @param args arguments presented by the user
	 * @return a processed form of the arguments presented by the user
	 * @throws IllegalArgumentException argument state is not what was expected
	 * @throws ParseException arguments could not be parsed
	 */

	public CommandLine process(String[] args)
		throws IllegalArgumentException, ParseException
	{
		BasicParser parser = new BasicParser();
		CommandLine line = parser.parse(this.options, args);

		if (this.truststoreFilenameOpt != null && this.truststorePasswordOpt != null) {
			String truststoreFilename = line.getOptionValue(SampleProperties.PROPERTY_TRUSTSTORE_FILENAME);
			String truststorePassword = line.getOptionValue(SampleProperties.PROPERTY_TRUSTSTORE_PASSWORD);

			if (truststoreFilename != null && truststorePassword == null) {
				throw new IllegalArgumentException("must specify a truststore password when specifying a truststore filename");
			}

			if (truststoreFilename == null && truststorePassword != null) {
				throw new IllegalArgumentException("must specify a truststore filename when specifying a truststore password");
			}
		}

		if (this.filterOpt != null) {
			String[] filterStrs = line.getOptionValues(SampleProperties.PROPERTY_FILTER);
			if (filterStrs != null) {
				for (String filterStr : filterStrs) {
					if (!Pattern.matches("[0-9]*[0-9][.][0-9]*[0-9][.][0-9]*[0-9][.][0-9]*[0-9]:[0-9]*[0-9][.][0-9]*[0-9][.][0-9]*[0-9][.][0-9]*[0-9]", filterStr)) {
						throw new IllegalArgumentException("illegal filter format");
					}
				}
			}
		}

		if (this.groupOpt != null) {
			Group g = Group.fromValue(line.getOptionValue(SampleProperties.PROPERTY_GROUP));
			if (g == null) {
				throw new IllegalArgumentException("illegal group");
			}
		}

		try {
			String startStr = line.getOptionValue(SampleProperties.PROPERTY_START);
			if (startStr != null) {
				SampleUtilities.parseTime(startStr);
			}
		} catch (java.text.ParseException e) {
			throw new IllegalArgumentException("unable to parse 'start'");
		}

		try {
			String endStr = line.getOptionValue(SampleProperties.PROPERTY_END);
			if (endStr != null) {
				SampleUtilities.parseTime(endStr);
			}
		} catch (java.text.ParseException e) {
			throw new IllegalArgumentException("unable to parse 'end'");
		}

		return line;
	}

	/**
	 * Retrieves a subnet content filter from the command line values.
	 * 
	 * @param line command line values
	 * @return subnet content filter, or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public SubnetContentFilter retrieveFilter(CommandLine line)
		throws IllegalArgumentException
	{
		SubnetContentFilter filter = null;
		String[] filterStrs = line.getOptionValues(SampleProperties.PROPERTY_FILTER);
		if (filterStrs != null) {
			filter = new SubnetContentFilter();
			for (String filterStr : filterStrs) {
				String[] split = filterStr.split(":");

				Subnet s = new Subnet();
				s.setNetworkIp(split[0]);
				s.setNetmask(split[1]);

				filter.getSubnets().add(s);
			}
		}

		return filter;
	}

	/**
	 * Retrieves a subnet content filter in string form from the command line values.
	 * 
	 * @param line command line values
	 * @return subnet content filter string, or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String retrieveFilterStr(CommandLine line)
		throws IllegalArgumentException
	{
		String[] filterStrs = line.getOptionValues(SampleProperties.PROPERTY_FILTER);
		if (filterStrs == null || filterStrs.length == 0) {
			return null;
		} else {
			String result = null;
			for (String filterStr : filterStrs) {
				if (result == null) {
					result = filterStr;
				} else {
					result += ", " + filterStr;
				}
			}

			return result;
		}
	}

	/**
	 * Retrieves the keystore filename from the command line values and properties.
	 * 
	 * @param line command line values
	 * @return the keystore filename or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String retrieveKeystoreFilename(CommandLine line)
		throws IllegalArgumentException
	{
		return line.getOptionValue(SampleProperties.PROPERTY_KEYSTORE_FILENAME, this.properties.getKeystoreFilename());
	}

	/**
	 * Retrieves the keystore filename from the command line values and properties.
	 * 
	 * @param line command line values
	 * @return the keystore filename or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String retrieveKeystorePassword(CommandLine line)
		throws IllegalArgumentException
	{
		return line.getOptionValue(SampleProperties.PROPERTY_KEYSTORE_PASSWORD, this.properties.getKeystorePassword());
	}

	/**
	 * Retrieves the truststore filename from the command line values and properties.
	 * 
	 * @param line command line values
	 * @return the truststore filename or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String retrieveTruststoreFilename(CommandLine line)
		throws IllegalArgumentException
	{
		return line.getOptionValue(SampleProperties.PROPERTY_TRUSTSTORE_FILENAME, this.properties.getTruststoreFilename());
	}

	/**
	 * Retrieves the truststore password from the command line values.
	 * 
	 * @param line command line values
	 * @return the truststore password or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String retrieveTruststorePassword(CommandLine line)
		throws IllegalArgumentException
	{
		return line.getOptionValue(SampleProperties.PROPERTY_TRUSTSTORE_PASSWORD, this.properties.getTruststorePassword());
	}

	/**
	 * Retrieves the pxGrid hostname filename from the command line values.
	 * 
	 * @param line command line values
	 * @return the pxGrid hostname or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String[] retrieveHostnames(CommandLine line)
		throws IllegalArgumentException
	{
		String[] hostnames = line.getOptionValues(SampleProperties.PROPERTY_HOSTNAME);
		if (hostnames != null) {
			return hostnames;
		} else {
			return this.properties.getHostnames();
		}
	}

	/**
	 * Retrieves the pxGrid username from the command line values.
	 * 
	 * @param line command line values
	 * @return the pxGrid username or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String retrieveUsername(CommandLine line)
		throws IllegalArgumentException
	{
		return line.getOptionValue(SampleProperties.PROPERTY_USERNAME, this.properties.getUsername());
	}

	/**
	 * Retrieves the pxGrid description from the command line values.
	 * 
	 * @param line command line values
	 * @return the pxGrid description or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public String retrieveDescription(CommandLine line)
		throws IllegalArgumentException
	{
		return line.getOptionValue(SampleProperties.PROPERTY_DESCRIPTION, this.properties.getDescription());
	}

	/**
	 * Retrieves the group from the command line values.
	 * 
	 * @param line command line values
	 * @return the group or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public Group retrieveGroup(CommandLine line)
		throws IllegalArgumentException
	{
		if (line.getOptionValue(SampleProperties.PROPERTY_GROUP) != null) {
			return Group.fromValue(line.getOptionValue(SampleProperties.PROPERTY_GROUP));
		} else {
			return Group.fromValue(this.properties.getGroup());
		}
	}

	/**
	 * Retrieves a start date/time from the command line.
	 * 
	 * @param line command line values
	 * @return the start or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public Calendar retrieveStart(CommandLine line)
		throws IllegalArgumentException, java.text.ParseException
	{
		if (line.getOptionValue(SampleProperties.PROPERTY_START) != null) {
			return SampleUtilities.parseTime(line.getOptionValue(SampleProperties.PROPERTY_START));
		} else {
			return null;
		}
	}

	/**
	 * Retrieves an end date/time from the command line.
	 * 
	 * @param line command line values
	 * @return the end or null if one wasn't specified
	 * @throws IllegalArgumentException
	 */

	public Calendar retrieveEnd(CommandLine line)
		throws IllegalArgumentException, java.text.ParseException
	{
		if (line.getOptionValue(SampleProperties.PROPERTY_END) != null) {
			return SampleUtilities.parseTime(line.getOptionValue(SampleProperties.PROPERTY_END));
		} else {
			return null;
		}
	}

	/**
	 * Prints help for the sample to STDOUT.
	 * 
	 * @param name name of the sample
	 */

	public void printHelp(String name) {
		HelpFormatter formatter = new HelpFormatter();
		formatter.setWidth(200);
		formatter.printHelp(name, this.options);
	}
}
