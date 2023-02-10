package com.cisco.pxgrid.samples.ise;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.File;
import java.util.Calendar;
import java.util.Properties;
import java.text.ParseException;

import org.apache.commons.io.FilenameUtils;

public class SampleProperties {
	public static final String SAMPLES_HOME = "samplesHome";
	public static final String SAMPLES_PROPERTIES = "samplesProperties";
	public static final String SAMPLES_VERSION = "samplesVersion";
	public static final String PROPERTY_HOSTNAME = "hostname";
	public static final String PROPERTY_USERNAME = "username";
	public static final String PROPERTY_DESCRIPTION = "description";
	public static final String PROPERTY_KEYSTORE_FILENAME = "keystoreFilename";
	public static final String PROPERTY_KEYSTORE_PASSWORD = "keystorePassword";
	public static final String PROPERTY_TRUSTSTORE_FILENAME = "truststoreFilename";
	public static final String PROPERTY_TRUSTSTORE_PASSWORD = "truststorePassword";
	public static final String PROPERTY_GROUP = "group";
	public static final String PROPERTY_FILTER = "filter";
	public static final String PROPERTY_START = "start";
	public static final String PROPERTY_END = "end";

	public static SampleProperties load()
		throws IOException, ParseException
	{
		String samplesHome = System.getProperty(SAMPLES_HOME);
		if (samplesHome == null) {
			throw new IOException("must specify system property samplesHome");
		}

		String samplesProperties = System.getProperty(SAMPLES_PROPERTIES);
		if (samplesProperties == null) {
			throw new IOException("must specify system property samplesProperties");
		}

		String samplesVersion = System.getProperty(SAMPLES_VERSION);
		if (samplesVersion == null) {
			throw new IOException("must specify system property samplesVersion");
		}

		SampleProperties sp = new SampleProperties();
		FileInputStream fis = new FileInputStream(samplesProperties);

		Properties props = new Properties();
		props.load(fis);
		fis.close();


		sp.setVersion(samplesVersion);

		if (props.getProperty(PROPERTY_HOSTNAME) != null) {
			String[] hostnames = props.getProperty(PROPERTY_HOSTNAME).split(",");
			for (int i=0; i < hostnames.length; i++) {
				hostnames[i] = hostnames[i].trim();
			}

			sp.setHostnames(hostnames);
		}

		sp.setUsername(props.getProperty(PROPERTY_USERNAME));
		sp.setDescription(props.getProperty(PROPERTY_DESCRIPTION));
		sp.setKeystoreFilename(props.getProperty(PROPERTY_KEYSTORE_FILENAME));
		sp.setKeystorePassword(props.getProperty(PROPERTY_KEYSTORE_PASSWORD));
		sp.setTruststoreFilename(props.getProperty(PROPERTY_TRUSTSTORE_FILENAME));
		sp.setTruststorePassword(props.getProperty(PROPERTY_TRUSTSTORE_PASSWORD));
		sp.setGroup(props.getProperty(PROPERTY_GROUP));
		sp.setFilter(props.getProperty(PROPERTY_FILTER));
		sp.setStart(SampleUtilities.parseTime(props.getProperty(PROPERTY_START)));
		sp.setEnd(SampleUtilities.parseTime(props.getProperty(PROPERTY_END)));


		// make relative filenames absolute

		if (sp.getKeystoreFilename() != null) {
			File keystoreFile = new File(sp.getKeystoreFilename());
			if (!keystoreFile.isAbsolute()) {
				File appended = new File(samplesHome, sp.getKeystoreFilename());
				sp.setKeystoreFilename(FilenameUtils.normalize(appended.toString()));
			}
		}

		if (sp.getTruststoreFilename() != null) {
			File truststoreFile = new File(sp.getTruststoreFilename());
			if (!truststoreFile.isAbsolute()) {
				File appended = new File(samplesHome, sp.getTruststoreFilename());
				sp.setTruststoreFilename(FilenameUtils.normalize(appended.toString()));
			}
		}

		return sp;
	}

	private String version;
	private String[] hostnames;
	private String username;
	private String description;
	private String keystoreFilename;
	private String keystorePassword;
	private String truststoreFilename;
	private String truststorePassword;
	private String group;
	private String filter;
	private Calendar start;
	private Calendar end;

	public String getVersion() {
		return this.version;
	}

	public void setVersion(String version) {
		this.version = version;
	}

	public String[] getHostnames() {
		return this.hostnames;
	}

	public void setHostnames(String[] hostnames) {
		this.hostnames = hostnames;
	}

	public String getUsername() {
		return this.username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getDescription() {
		return this.description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getKeystoreFilename() {
		return this.keystoreFilename;
	}

	public void setKeystoreFilename(String keystoreFilename) {
		this.keystoreFilename = keystoreFilename;
	}

	public String getKeystorePassword() {
		return this.keystorePassword;
	}

	public void setKeystorePassword(String keystorePassword) {
		this.keystorePassword = keystorePassword;
	}

	public String getTruststoreFilename() {
		return this.truststoreFilename;
	}

	public void setTruststoreFilename(String truststoreFilename) {
		this.truststoreFilename = truststoreFilename;
	}

	public String getTruststorePassword() {
		return this.truststorePassword;
	}

	public void setTruststorePassword(String truststorePassword) {
		this.truststorePassword = truststorePassword;
	}

	public String getGroup() {
		return this.group;
	}

	public void setGroup(String group) {
		this.group = group;
	}

	public String getFilter() {
		return this.filter;
	}

	public void setFilter(String filter) {
		this.filter = filter;
	}

	public Calendar getStart() {
		return this.start;
	}

	public void setStart(Calendar start) {
		this.start = start;
	}

	public Calendar getEnd() {
		return this.end;
	}

	public void setEnd(Calendar end) {
		this.end = end;
	}
}
