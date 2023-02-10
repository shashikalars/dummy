package com.cisco.pxgrid.samples.ise;

import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;

import javax.net.ssl.X509TrustManager;

/**
 * For the samples, use a simple trust manager that trusts everything. A real
 * implementation will do more checking.
 * 
 * @author jangwin
 *
 */

public class SampleTrustManager
	implements X509TrustManager
{
	@Override
	public X509Certificate[] getAcceptedIssuers() {
		return null;
	}

	@Override
	public void checkServerTrusted(X509Certificate[] arg0, String arg1)
		throws CertificateException
	{
	}

	@Override
	public void checkClientTrusted(X509Certificate[] arg0, String arg1)
		throws CertificateException
	{
	}
};
