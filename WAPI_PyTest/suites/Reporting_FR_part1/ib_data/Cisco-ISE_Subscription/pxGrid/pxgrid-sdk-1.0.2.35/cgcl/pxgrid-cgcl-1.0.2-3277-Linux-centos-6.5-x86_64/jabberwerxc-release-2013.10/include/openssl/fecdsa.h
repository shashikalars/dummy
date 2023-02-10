/*------------------------------------------------------------------
 * crypto/fec/fecdsa.h - Digital signature definitions used by the Fundamental
 * Elliptic Curve Cryptography algorithms
 *
 * June, 2011
 *
 * Copyright (c) 2011,2012 by cisco Systems, Inc.
 * All rights reserved.
 *------------------------------------------------------------------
 */
#ifndef HEADER_FECDSA_H
#define HEADER_FECDSA_H

#include <openssl/opensslconf.h>

#ifdef OPENSSL_NO_CISCO_FECDSA
#error CISCO_FECDSA is disabled.
#endif

#include <openssl/fec.h>
#include <openssl/ossl_typ.h>
#ifndef OPENSSL_NO_DEPRECATED
#include <openssl/bn.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ECDSA_SIG_st
	{
	BIGNUM *r;
	BIGNUM *s;
	} ECDSA_SIG;

/** ECDSA_SIG *ECDSA_SIG_new(void)
 * allocates and initialize a ECDSA_SIG structure
 * \return pointer to a ECDSA_SIG structure or NULL if an error occurred
 */
ECDSA_SIG *ECDSA_SIG_new(void);

/** ECDSA_SIG_free
 * frees a ECDSA_SIG structure
 * \param a pointer to the ECDSA_SIG structure
 */
void	  ECDSA_SIG_free(ECDSA_SIG *a);

/** i2d_ECDSA_SIG
 * DER encode content of ECDSA_SIG object (note: this function modifies *pp
 * (*pp += length of the DER encoded signature)).
 * \param a  pointer to the ECDSA_SIG object
 * \param pp pointer to a unsigned char pointer for the output or NULL
 * \return the length of the DER encoded ECDSA_SIG object or 0 
 */
int	  i2d_KTI_SIG(const ECDSA_SIG *a, unsigned char **pp);

/** d2i_ECDSA_SIG
 * decodes a DER encoded ECDSA signature (note: this function changes *pp
 * (*pp += len)). 
 * \param v pointer to ECDSA_SIG pointer (may be NULL)
 * \param pp buffer with the DER encoded signature
 * \param len bufferlength
 * \return pointer to the decoded ECDSA_SIG structure (or NULL)
 */
ECDSA_SIG *d2i_KTI_SIG(ECDSA_SIG **v, const unsigned char **pp, long len);

/** ECDSA_do_sign
 * computes the ECDSA signature of the given hash value using
 * the supplied private key and returns the created signature.
 * \param dgst pointer to the hash value
 * \param dgst_len length of the hash value
 * \param eckey pointer to the EC_KEY object containing a private EC key
 * \return pointer to a ECDSA_SIG structure or NULL
 */
ECDSA_SIG *ECDSA_do_sign(const unsigned char *dgst,int dgst_len,EC_KEY *eckey);

/** ECDSA_do_verify
 * verifies that the supplied signature is a valid ECDSA
 * signature of the supplied hash value using the supplied public key.
 * \param dgst pointer to the hash value
 * \param dgst_len length of the hash value
 * \param sig  pointer to the ECDSA_SIG structure
 * \param eckey pointer to the EC_KEY object containing a public EC key
 * \return 1 if the signature is valid, 0 if the signature is invalid and -1 on error
 */
int	  ECDSA_do_verify(const unsigned char *dgst, int dgst_len,
		const ECDSA_SIG *sig, EC_KEY* eckey);

const ECDSA_METHOD *ECDSA_OpenSSL(void);

/** ECDSA_set_default_method
 * sets the default ECDSA method
 * \param meth the new default ECDSA_METHOD
 */
void	  ECDSA_set_default_method(const ECDSA_METHOD *meth);

/** ECDSA_get_default_method
 * returns the default ECDSA method
 * \return pointer to ECDSA_METHOD structure containing the default method
 */
const ECDSA_METHOD *ECDSA_get_default_method(void);

/** ECDSA_set_method
 * sets method to be used for the ECDSA operations
 * \param eckey pointer to the EC_KEY object
 * \param meth  pointer to the new method
 * \return 1 on success and 0 otherwise 
 */
int 	  ECDSA_set_method(EC_KEY *eckey, const ECDSA_METHOD *meth);

/** ECDSA_size
 * returns the maximum length of the DER encoded signature
 * \param  eckey pointer to a EC_KEY object
 * \return numbers of bytes required for the DER encoded signature
 */
int	  ECDSA_size(const EC_KEY *eckey);

/** ECDSA_sign_setup
 * precompute parts of the signing operation. 
 * \param eckey pointer to the EC_KEY object containing a private EC key
 * \param ctx  pointer to a BN_CTX object (may be NULL)
 * \param kinv pointer to a BIGNUM pointer for the inverse of k
 * \param rp   pointer to a BIGNUM pointer for x coordinate of k * generator
 * \return 1 on success and 0 otherwise
 */
int 	  ECDSA_sign_setup(EC_KEY *eckey, BN_CTX *ctx, BIGNUM **kinv, 
		BIGNUM **rp);

/** ECDSA_sign
 * computes ECDSA signature of a given hash value using the supplied
 * private key (note: sig must point to ECDSA_size(eckey) bytes of memory).
 * \param type this parameter is ignored
 * \param dgst pointer to the hash value to sign
 * \param dgstlen length of the hash value
 * \param sig buffer to hold the DER encoded signature
 * \param siglen pointer to the length of the returned signature
 * \param eckey pointer to the EC_KEY object containing a private EC key
 * \return 1 on success and 0 otherwise
 */
int	  ECDSA_sign(int type, const unsigned char *dgst, int dgstlen, 
		unsigned char *sig, unsigned int *siglen, EC_KEY *eckey);


/** ECDSA_verify
 * verifies that the given signature is valid ECDSA signature
 * of the supplied hash value using the specified public key.
 * \param type this parameter is ignored
 * \param dgst pointer to the hash value 
 * \param dgstlen length of the hash value
 * \param sig  pointer to the DER encoded signature
 * \param siglen length of the DER encoded signature
 * \param eckey pointer to the EC_KEY object containing a public EC key
 * \return 1 if the signature is valid, 0 if the signature is invalid and -1 on error
 */
int 	  ECDSA_verify(int type, const unsigned char *dgst, int dgstlen, 
		const unsigned char *sig, int siglen, EC_KEY *eckey);

/* the standard ex_data functions */
int 	  ECDSA_get_ex_new_index(long argl, void *argp, CRYPTO_EX_new 
		*new_func, CRYPTO_EX_dup *dup_func, CRYPTO_EX_free *free_func);
int 	  ECDSA_set_ex_data(EC_KEY *d, int idx, void *arg);
void 	  *ECDSA_get_ex_data(EC_KEY *d, int idx);


struct ecdsa_method {
    const char *name;
    ECDSA_SIG *(*ecdsa_do_sign)(const unsigned char *dgst, int dgst_len, 
                                const BIGNUM *inv, const BIGNUM *rp, EC_KEY *eckey);
    int (*ecdsa_sign_setup)(EC_KEY *eckey, BN_CTX *ctx, BIGNUM **kinv, 
                            BIGNUM **r);
    int (*ecdsa_do_verify)(const unsigned char *dgst, int dgst_len, 
                           const ECDSA_SIG *sig, EC_KEY *eckey);
    
    int flags;
    char *app_data;
};

/* If this flag is set the ECDSA method is FIPS compliant and can be used
 * in FIPS mode. This is set in the validated module method. If an
 * application sets this flag in its own methods it is its responsibility
 * to ensure the result is compliant.
 */
#define ECDSA_FLAG_FIPS_METHOD  0x1

typedef struct ecdsa_data_st {
	/* EC_KEY_METH_DATA part */
	int (*init)(EC_KEY *);
	/* method (ECDSA) specific part */
	ENGINE	*engine;
	int	flags;
	const ECDSA_METHOD *meth;
	CRYPTO_EX_DATA ex_data;
} ECDSA_DATA;

/** ecdsa_check
 * checks whether ECKEY->meth_data is a pointer to a ECDSA_DATA structure
 * and if not it removes the old meth_data and creates a ECDSA_DATA structure.
 * \param  eckey pointer to a EC_KEY object
 * \return pointer to a ECDSA_DATA structure
 */
ECDSA_DATA *ecdsa_check(EC_KEY *eckey);

 
#ifdef  __cplusplus
}
#endif
#endif
