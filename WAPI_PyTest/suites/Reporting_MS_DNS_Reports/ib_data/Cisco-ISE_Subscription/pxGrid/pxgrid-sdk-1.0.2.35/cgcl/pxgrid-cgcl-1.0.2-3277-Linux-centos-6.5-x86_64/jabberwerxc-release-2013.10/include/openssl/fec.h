/*------------------------------------------------------------------
 * crypto/fec/fec.h - Define OpenSSL API to interface with the Fundamental
 * Elliptic Curve Cryptography algorithms
 *
 * June, 2011
 *
 * Copyright (c) 2011,2012 by cisco Systems, Inc.
 * All rights reserved.
 *------------------------------------------------------------------
 */
#ifndef HEADER_FEC_H
#define HEADER_FEC_H

#include <openssl/opensslconf.h>

#ifdef OPENSSL_NO_CISCO_FEC
#error CISCO_FEC is disabled.
#endif

#include <openssl/asn1.h>
#include <openssl/symhacks.h>
#ifndef OPENSSL_NO_DEPRECATED
#include <openssl/bn.h>
#endif


#ifdef  __cplusplus
extern "C" {
#elif defined(__SUNPRO_C)
# if __SUNPRO_C >= 0x520
# pragma error_messages (off,E_ARRAY_OF_INCOMPLETE_NONAME,E_ARRAY_OF_INCOMPLETE)
# endif
# endif


/*
 * The follow definitions and prototypes are required to glue to the
 * Fundamental Ellipitcal Curve implementation to the existing OPENSSL API
 */
#define OPENSSL_EC_NAMED_CURVE  0x001
#define EC_PKEY_NO_PARAMETERS   0x001
#define EC_PKEY_NO_PUBKEY	0x002

#ifndef OPENSSL_ECC_MAX_FIELD_BITS
#define OPENSSL_ECC_MAX_FIELD_BITS 661
#endif

/* some values for the flags field */
#define EC_FLAG_NON_FIPS_ALLOW	0x1
#define EC_FLAG_FIPS_CHECKED	0x2

typedef enum {
        /* values as defined in X9.62 (ECDSA) and elsewhere */
        POINT_CONVERSION_COMPRESSED = 2,
        POINT_CONVERSION_UNCOMPRESSED = 4,
        POINT_CONVERSION_HYBRID = 6
} point_conversion_form_t;

typedef struct ec_curve_data_st  EC_CURVE_DATA;

typedef struct {
   int nid;
   const char *comment;
} EC_builtin_curve;
size_t EC_get_builtin_curves(EC_builtin_curve *r, size_t nitems);

/* Structure details are not part of the exported interface,
 * so all this may change in future versions. */

    
typedef struct ec_method_st EC_METHOD;

typedef struct ec_group_st EC_GROUP;
typedef struct ec_point_st EC_POINT;
typedef struct ec_key_st EC_KEY;

const EC_GROUP   *EC_KEY_get0_group(const EC_KEY *);
EC_KEY           *EC_KEY_dup(const EC_KEY *);
int               EC_KEY_set_group(EC_KEY *, const EC_GROUP *);
const EC_POINT   *EC_KEY_get0_public_key(const EC_KEY *);
const BIGNUM     *EC_KEY_get0_private_key(const EC_KEY *);
int               EC_KEY_set_public_key(EC_KEY *, const EC_POINT *);
int               EC_KEY_set_private_key(EC_KEY *, const BIGNUM *);
unsigned          EC_KEY_get_enc_flags(const EC_KEY *);
void              EC_KEY_set_enc_flags(EC_KEY *, unsigned int); 
int               EC_KEY_up_ref(EC_KEY *);
EC_KEY           *EC_KEY_new(void);
void              EC_KEY_free(EC_KEY *);
int               EC_KEY_generate_key(EC_KEY *);
int		  EC_KEY_set_public_key_affine_coordinates(EC_KEY *key, 
	                                     BIGNUM *x, BIGNUM *y);
void              EC_KEY_set_conv_form(EC_KEY *, point_conversion_form_t);
void              EC_KEY_set_asn1_flag(EC_KEY *, int);
EC_KEY           *EC_KEY_new_by_curve_name(int nid);
int               EC_KEY_precompute_mult(EC_KEY *, BN_CTX *ctx);
void             *EC_KEY_get_key_method_data(EC_KEY *, void *(*dup_func)(void *), 
                                             void (*free_func)(void *), 
                                             void (*clear_free_func)(void *));
void              EC_KEY_insert_key_method_data(EC_KEY *, void *data, 
                                                void *(*dup_func)(void *), 
                                                void (*free_func)(void *), 
                                                void (*clear_free_func)(void *));
EC_KEY           *EC_KEY_copy(EC_KEY *dest, const EC_KEY *src);
int               EC_KEY_get_flags(const EC_KEY *key);
void              EC_KEY_set_flags(EC_KEY *key, int flags);
void              EC_KEY_clear_flags(EC_KEY *key, int flags);

EC_GROUP         *EC_GROUP_new(const EC_METHOD *meth);
EC_GROUP         *EC_GROUP_new_curve_from_hex_data(int, EC_CURVE_DATA*);
int               EC_GROUP_get_order(const EC_GROUP *, BIGNUM *order, BN_CTX *);
EC_GROUP         *EC_GROUP_dup(const EC_GROUP *);
int               EC_GROUP_copy(EC_GROUP *dest, const EC_GROUP *src);
void              EC_GROUP_free(EC_GROUP *);
void              EC_GROUP_clear_free(EC_GROUP *);
int               EC_GROUP_cmp(const EC_GROUP *, const EC_GROUP *, BN_CTX *);
EC_GROUP         *EC_GROUP_new_by_curve_name(int nid);
int               EC_GROUP_get_asn1_flag(const EC_GROUP *);
void              EC_GROUP_set_asn1_flag(EC_GROUP *, int flag);
const EC_POINT   *EC_GROUP_get0_generator(const EC_GROUP *);
unsigned char    *EC_GROUP_get0_seed(const EC_GROUP *);
int               EC_GROUP_get_curve_name(const EC_GROUP *);
void              EC_GROUP_set_curve_name (EC_GROUP *group, int nid);
size_t            EC_GROUP_get_seed_len(const EC_GROUP *);
int               EC_GROUP_get_basis_type(const EC_GROUP *);
const EC_METHOD  *EC_GROUP_method_of(const EC_GROUP *);
int               EC_GROUP_get_curve_GF2m(const EC_GROUP *, BIGNUM *p, 
                               BIGNUM *a, BIGNUM *b, BN_CTX *);
int               EC_GROUP_get_curve_GFp(const EC_GROUP *, BIGNUM *p, 
                               BIGNUM *a, BIGNUM *b, BN_CTX *);
int               EC_GROUP_get_cofactor(const EC_GROUP *, BIGNUM *cofactor, 
                               BN_CTX *);
int               EC_GROUP_get_degree(const EC_GROUP *);
void              EC_GROUP_set_point_conversion_form(EC_GROUP *, 
                               point_conversion_form_t);
size_t            EC_GROUP_set_seed(EC_GROUP *, const unsigned char *, 
                               size_t len);
int               EC_GROUP_check(const EC_GROUP *group, BN_CTX *ctx);
EC_GROUP         *EC_GROUP_new_curve_GFp (const BIGNUM *p, const BIGNUM *a,
                                          const BIGNUM *b, BN_CTX *ctx);
int               EC_GROUP_precompute_mult(EC_GROUP *group, BN_CTX *ctx);
int               EC_GROUP_have_precompute_mult(const EC_GROUP *group);
int               EC_GROUP_set_generator(EC_GROUP *group,
                                         const EC_POINT *generator,
                                         const BIGNUM *order, 
                                         const BIGNUM *cofactor);

point_conversion_form_t EC_GROUP_get_point_conversion_form(const EC_GROUP *);
point_conversion_form_t EC_KEY_get_conv_form(const EC_KEY *);

EC_POINT         *EC_POINT_new(const EC_GROUP *);
int               EC_POINT_copy(EC_POINT *, const EC_POINT *);
void              EC_POINT_free(EC_POINT *);
void              EC_POINT_clear_free(EC_POINT *);
int               EC_POINT_mul(const EC_GROUP *, EC_POINT *r, const BIGNUM *,
                           const EC_POINT *, const BIGNUM *, BN_CTX *);
int               EC_POINT_cmp(const EC_GROUP *, const EC_POINT *a, 
                           const EC_POINT *b, BN_CTX *);
BIGNUM           *EC_POINT_point2bn(const EC_GROUP *, const EC_POINT *, 
                           point_conversion_form_t form, BIGNUM *, BN_CTX *);
EC_POINT         *EC_POINT_bn2point(const EC_GROUP *, const BIGNUM *,
                                    EC_POINT *, BN_CTX *);
size_t            EC_POINT_point2oct(const EC_GROUP *, const EC_POINT *, 
                                     point_conversion_form_t form, 
                                     unsigned char *buf,
                                     size_t len, BN_CTX *);
char             *EC_POINT_point2hex(const EC_GROUP *, const EC_POINT *,
                                     point_conversion_form_t form, BN_CTX *);
EC_POINT         *EC_POINT_hex2point(const EC_GROUP *, const char *,
                                     EC_POINT *, BN_CTX *);
int               EC_POINT_oct2point(const EC_GROUP *, EC_POINT *,
                           const unsigned char *buf, size_t len, BN_CTX *);
int               EC_POINT_is_at_infinity(const EC_GROUP *group, 
                                          const EC_POINT *point);
int               EC_POINT_set_to_infinity(const EC_GROUP *group, 
                                           EC_POINT *point);
const EC_METHOD  *EC_POINT_method_of(const EC_POINT *point);
int               EC_POINT_get_Jprojective_coordinates_GFp(const EC_GROUP *group, 
                                                           const EC_POINT *point,
                                                           BIGNUM *x, BIGNUM *y, 
                                                           BIGNUM *z, BN_CTX *ctx);
int               EC_POINT_set_Jprojective_coordinates_GFp(const EC_GROUP *group, 
                                                           EC_POINT *point, 
                                                           const BIGNUM *x, 
                                                           const BIGNUM *y, 
                                                           const BIGNUM *z, 
                                                           BN_CTX *ctx);
int               EC_POINT_get_affine_coordinates_GFp (const EC_GROUP *group, 
                                                       const EC_POINT *point,
                                                       BIGNUM *x, BIGNUM *y, 
                                                       BN_CTX *ctx);
int               EC_POINT_set_affine_coordinates_GFp (const EC_GROUP *group, 
                                                       EC_POINT *point,
                                                       const BIGNUM *x, 
                                                       const BIGNUM *y, 
                                                       BN_CTX *ctx);
int               EC_POINT_set_compressed_coordinates_GFp(const EC_GROUP *group, 
                                                          EC_POINT *point,
                                                          const BIGNUM *x, 
                                                          int y_bit, BN_CTX *ctx);
int               EC_POINT_set_compressed_coordinates_GF2m(const EC_GROUP *group, 
                                                           EC_POINT *point,
                                                           const BIGNUM *x, 
                                                           int y_bit, BN_CTX *ctx);
int               EC_POINT_make_affine(const EC_GROUP *, EC_POINT *, BN_CTX *);
int               EC_POINTs_make_affine(const EC_GROUP *group, size_t num, 
                                        EC_POINT *points[], BN_CTX *ctx);
int               EC_POINT_add(const EC_GROUP *, EC_POINT *r, const EC_POINT *a, 
                               const EC_POINT *b, BN_CTX *);
int               EC_POINT_dbl(const EC_GROUP *, EC_POINT *r, const EC_POINT *a, 
                               BN_CTX *);
int               EC_POINT_invert(const EC_GROUP *, EC_POINT *, BN_CTX *);

int               EC_METHOD_get_field_type(const EC_METHOD *);

EC_KEY   *d2i_ECParameters(EC_KEY **a, const unsigned char **in, long len);
EC_KEY   *d2i_ECPrivateKey(EC_KEY **a, const unsigned char **in, long len);
EC_KEY   *o2i_ECPublicKey(EC_KEY **a, const unsigned char **in, long len);
int       i2d_ECParameters(EC_KEY *a, unsigned char **out);
int       i2d_ECPrivateKey(EC_KEY *a, unsigned char **out);
int       i2o_ECPublicKey(EC_KEY *a, unsigned char **out);
EC_GROUP *d2i_ECPKParameters(EC_GROUP **, const unsigned char **in, long len);
int       i2d_ECPKParameters(const EC_GROUP *, unsigned char **out);

#define ECParameters_dup(x) ASN1_dup_of(EC_KEY,i2d_ECParameters,d2i_ECParameters,x)
#define d2i_ECPKParameters_fp(fp,x) (EC_GROUP *)ASN1_d2i_fp(NULL, \
                                    (char *(*)())d2i_ECPKParameters,(fp), \
                                    (unsigned char **)(x))
#define i2d_ECPKParameters_fp(fp,x) ASN1_i2d_fp(i2d_ECPKParameters,(fp), \
                                               (unsigned char *)(x))
/* 
 * EC_METHODs for curves over GF(p).
 * FEC does not provide these optimizations
 */
const EC_METHOD *EC_GFp_simple_method(void);
const EC_METHOD *EC_GFp_mont_method(void);
const EC_METHOD *EC_GFp_nist_method(void);
const EC_METHOD *EC_GF2m_simple_method(void);

#define d2i_ECPKParameters_bio(bp,x) ASN1_d2i_bio_of(EC_GROUP,NULL,d2i_ECPKParameters,bp,x)
#define i2d_ECPKParameters_bio(bp,x) ASN1_i2d_bio_of_const(EC_GROUP,i2d_ECPKParameters,bp,x)

#ifndef OPENSSL_NO_BIO
int     ECParameters_print(BIO *bp, const EC_KEY *x);
int     EC_KEY_print(BIO *bp, const EC_KEY *x, int off);
int     ECPKParameters_print(BIO *bp, const EC_GROUP *x, int off);
#endif
#ifndef OPENSSL_NO_FP_API
int     ECParameters_print_fp(FILE *fp, const EC_KEY *x);
int     EC_KEY_print_fp(FILE *fp, const EC_KEY *x, int off);
int     ECPKParameters_print_fp(FILE *fp, const EC_GROUP *x, int off);
#endif  


#ifndef __cplusplus
#if defined(__SUNPRO_C)
#  if __SUNPRO_C >= 0x520
# pragma error_messages (default,E_ARRAY_OF_INCOMPLETE_NONAME,E_ARRAY_OF_INCOMPLETE)
#  endif
# endif
#endif

/* BEGIN ERROR CODES */
/* The following lines are auto generated by the script mkerr.pl. Any changes
 * made after this point may be overwritten when the script is next run.
 */
void ERR_load_FEC_strings(void);

/* Error codes for the FEC functions. */

/* Function codes. */
#define FEC_F_D2I_ECPARAMETERS				 99
#define FEC_F_D2I_ECPKPARAMETERS			 100
#define FEC_F_D2I_ECPRIVATEKEY				 101
#define FEC_F_DO_EC_KEY_PRINT				 203
#define FEC_F_DO_FEC_KEY_PRINT				 232
#define FEC_F_ECDH_COMPUTE_KEY				 102
#define FEC_F_ECDSA_CHECK				 218
#define FEC_F_ECDSA_DATA_NEW_METHOD			 196
#define FEC_F_ECDSA_DO_SIGN				 103
#define FEC_F_ECDSA_DO_SIGN_EX				 202
#define FEC_F_ECDSA_DO_VERIFY				 104
#define FEC_F_ECDSA_SIGN				 105
#define FEC_F_ECDSA_SIGN_EX				 201
#define FEC_F_ECDSA_SIGN_SETUP				 193
#define FEC_F_ECDSA_SIZE				 106
#define FEC_F_ECDSA_VERIFY				 107
#define FEC_F_ECKEY_PARAM2TYPE				 204
#define FEC_F_ECKEY_PARAM_DECODE			 205
#define FEC_F_ECKEY_PRIV_DECODE				 206
#define FEC_F_ECKEY_PRIV_ENCODE				 207
#define FEC_F_ECKEY_PUB_DECODE				 208
#define FEC_F_ECKEY_PUB_ENCODE				 209
#define FEC_F_ECKEY_TYPE2PARAM				 210
#define FEC_F_ECPARAMETERS_PRINT			 108
#define FEC_F_ECPARAMETERS_PRINT_FP			 109
#define FEC_F_ECPKPARAMETERS_PRINT			 110
#define FEC_F_ECPKPARAMETERS_PRINT_FP			 111
#define FEC_F_EC_ASN1_GROUP2PKPARAMETERS		 112
#define FEC_F_EC_ASN1_PARAMETERS2GROUP			 113
#define FEC_F_EC_ASN1_PKPARAMETERS2GROUP		 114
#define FEC_F_EC_DIFFIE_HELLMAN_COMPACT_OUTPUT		 115
#define FEC_F_EC_DIFFIE_HELLMAN_FULL_OUTPUT		 116
#define FEC_F_EC_EX_DATA_SET_DATA			 198
#define FEC_F_EC_GF2M_SIMPLE_METHOD			 180
#define FEC_F_EC_GFP_MONT_METHOD			 177
#define FEC_F_EC_GFP_NIST_METHOD			 178
#define FEC_F_EC_GFP_SIMPLE_GROUP_SET_CURVE		 117
#define FEC_F_EC_GFP_SIMPLE_METHOD			 179
#define FEC_F_EC_GROUP_CHECK				 118
#define FEC_F_EC_GROUP_CHECK_DISCRIMINANT		 119
#define FEC_F_EC_GROUP_CMP				 120
#define FEC_F_EC_GROUP_DUP				 121
#define FEC_F_EC_GROUP_GET0_GENERATOR			 122
#define FEC_F_EC_GROUP_GET0_SEED			 123
#define FEC_F_EC_GROUP_GET_BASIS_TYPE			 124
#define FEC_F_EC_GROUP_GET_COFACTOR			 125
#define FEC_F_EC_GROUP_GET_CURVE_GF2M			 126
#define FEC_F_EC_GROUP_GET_CURVE_GFP			 127
#define FEC_F_EC_GROUP_GET_CURVE_NAME			 128
#define FEC_F_EC_GROUP_GET_DEGREE			 129
#define FEC_F_EC_GROUP_GET_ORDER			 130
#define FEC_F_EC_GROUP_GET_SEED_LEN			 131
#define FEC_F_EC_GROUP_HAVE_PRECOMPUTE_MULT		 188
#define FEC_F_EC_GROUP_METHOD_OF			 132
#define FEC_F_EC_GROUP_NEW_CURVE_FROM_HEX_DATA		 133
#define FEC_F_EC_GROUP_NEW_CURVE_GF2M			 134
#define FEC_F_EC_GROUP_NEW_CURVE_GFP			 135
#define FEC_F_EC_GROUP_PRECOMPUTE_MULT			 136
#define FEC_F_EC_GROUP_SET_CURVE_GF2M			 137
#define FEC_F_EC_GROUP_SET_CURVE_GFP			 138
#define FEC_F_EC_GROUP_SET_CURVE_NAME			 139
#define FEC_F_EC_GROUP_SET_GENERATOR			 140
#define FEC_F_EC_GROUP_SET_POINT_CONVERSION_FORM	 141
#define FEC_F_EC_GROUP_SET_SEED				 142
#define FEC_F_EC_INSERT_KEY_METHOD_DATA			 182
#define FEC_F_EC_KEYPAIR_TEST				 197
#define FEC_F_EC_KEY_CHECK_KEY				 195
#define FEC_F_EC_KEY_COPY				 191
#define FEC_F_EC_KEY_DUP				 143
#define FEC_F_EC_KEY_GENERATE_KEY			 144
#define FEC_F_EC_KEY_GET0_GROUP				 145
#define FEC_F_EC_KEY_GET0_PRIVATE_KEY			 146
#define FEC_F_EC_KEY_GET0_PUBLIC_KEY			 147
#define FEC_F_EC_KEY_GET_KEY_METHOD_DATA		 183
#define FEC_F_EC_KEY_NEW				 148
#define FEC_F_EC_KEY_NEW_BY_CURVE_NAME			 149
#define FEC_F_EC_KEY_PRECOMPUTE_MULT			 150
#define FEC_F_EC_KEY_PRINT				 151
#define FEC_F_EC_KEY_PRINT_FP				 152
#define FEC_F_EC_KEY_SET_ASN1_FLAG			 153
#define FEC_F_EC_KEY_SET_CONV_FORM			 154
#define FEC_F_EC_KEY_SET_ENC_FLAGS			 155
#define FEC_F_EC_KEY_SET_GROUP				 156
#define FEC_F_EC_KEY_SET_PRIVATE_KEY			 157
#define FEC_F_EC_KEY_SET_PUBLIC_KEY			 158
#define FEC_F_EC_KEY_SET_PUBLIC_KEY_AFFINE_COORDINATES	 234
#define FEC_F_EC_POINTS_MAKE_AFFINE			 189
#define FEC_F_EC_POINT_					 200
#define FEC_F_EC_POINT_BN2POINT				 159
#define FEC_F_EC_POINT_COPY				 160
#define FEC_F_EC_POINT_DUP				 161
#define FEC_F_EC_POINT_GET_AFFINE_COORDINATES_GF2M	 162
#define FEC_F_EC_POINT_GET_AFFINE_COORDINATES_GFP	 163
#define FEC_F_EC_POINT_GET_JPROJECTIVE_COORDINATES_GFP	 184
#define FEC_F_EC_POINT_INVERT				 192
#define FEC_F_EC_POINT_MAKE_AFFINE			 190
#define FEC_F_EC_POINT_METHOD_OF			 181
#define FEC_F_EC_POINT_MUL				 164
#define FEC_F_EC_POINT_NEW				 165
#define FEC_F_EC_POINT_OCT2POINT			 166
#define FEC_F_EC_POINT_POINT2BN				 167
#define FEC_F_EC_POINT_POINT2OCT			 168
#define FEC_F_EC_POINT_SET_AFFINE_COORDINATES_GF2M	 169
#define FEC_F_EC_POINT_SET_AFFINE_COORDINATES_GFP	 170
#define FEC_F_EC_POINT_SET_COMPRESSED_COORDINATES_GF2M	 185
#define FEC_F_EC_POINT_SET_COMPRESSED_COORDINATES_GFP	 186
#define FEC_F_EC_POINT_SET_JPROJECTIVE_COORDINATES_GFP	 187
#define FEC_F_FECKEY_PARAM2TYPE				 219
#define FEC_F_FECKEY_PARAM_DECODE			 220
#define FEC_F_FECKEY_PRIV_DECODE			 221
#define FEC_F_FECKEY_PRIV_ENCODE			 222
#define FEC_F_FECKEY_PUB_DECODE				 223
#define FEC_F_FECKEY_PUB_ENCODE				 224
#define FEC_F_FECKEY_TYPE2PARAM				 225
#define FEC_F_FEC_FIPS_CHECK_PRNG			 235
#define FEC_F_FEC_POINT_POINT2OCT			 199
#define FEC_F_I2D_ECPARAMETERS				 171
#define FEC_F_I2D_ECPKPARAMETERS			 172
#define FEC_F_I2D_ECPRIVATEKEY				 173
#define FEC_F_I2O_ECPUBLICKEY				 174
#define FEC_F_KTI_SIGN					 194
#define FEC_F_KTI_SIGN_WITH_K				 236
#define FEC_F_KTI_VERIFY				 175
#define FEC_F_O2I_ECPUBLICKEY				 176
#define FEC_F_OLD_EC_PRIV_DECODE			 211
#define FEC_F_OLD_FEC_PRIV_DECODE			 233
#define FEC_F_PKEY_EC_CTRL				 212
#define FEC_F_PKEY_EC_CTRL_STR				 213
#define FEC_F_PKEY_EC_DERIVE				 214
#define FEC_F_PKEY_EC_KEYGEN				 215
#define FEC_F_PKEY_EC_PARAMGEN				 216
#define FEC_F_PKEY_EC_SIGN				 217
#define FEC_F_PKEY_FEC_CTRL				 226
#define FEC_F_PKEY_FEC_CTRL_STR				 227
#define FEC_F_PKEY_FEC_DERIVE				 228
#define FEC_F_PKEY_FEC_KEYGEN				 229
#define FEC_F_PKEY_FEC_PARAMGEN				 230
#define FEC_F_PKEY_FEC_SIGN				 231

/* Reason codes. */
#define FEC_R_ALPHA_MALLOC_FAILED			 99
#define FEC_R_ASN1_ERROR				 100
#define FEC_R_BN2BIN_FAILED				 101
#define FEC_R_BN_CMP_FAILED				 102
#define FEC_R_BN_MALLOC_FAILED				 103
#define FEC_R_BN_OP_FAILED				 104
#define FEC_R_BUFFER_CALC_MISMATCH			 105
#define FEC_R_BUFFER_TOO_SMALL				 147
#define FEC_R_COFACTOR_NOT_ONE				 143
#define FEC_R_CONSISTENCY_TEST_FAILED			 145
#define FEC_R_COORDINATES_OUT_OF_RANGE			 1500
#define FEC_R_COPY_FAILED				 106
#define FEC_R_CTX_FAILED				 107
#define FEC_R_CURVE_MISMATCH				 108
#define FEC_R_D2I_ECPKPARAMETERS_FAILURE		 109
#define FEC_R_D2I_KTI_FAILED				 110
#define FEC_R_DECODE_ERROR				 146
#define FEC_R_EC_GROUP_NEW_BY_NAME_FAILURE		 111
#define FEC_R_FEC_ERROR					 142
#define FEC_R_FIELD_TOO_LARGE				 112
#define FEC_R_GENERATOR_IS_NOT_ON_CURVE			 113
#define FEC_R_GROUP2PKPARAMETERS_FAILURE		 114
#define FEC_R_GROUP_ELEM_MALLOC_FAILED			 115
#define FEC_R_I2D_ECPKPARAMETERS_FAILURE		 116
#define FEC_R_INSUFFICIENT_RETURN_LEN			 117
#define FEC_R_INVALID_CURVE				 148
#define FEC_R_INVALID_DIGEST_TYPE			 149
#define FEC_R_INVALID_ENCODING				 118
#define FEC_R_INVALID_FIELD				 119
#define FEC_R_INVALID_FORM				 120
#define FEC_R_INVALID_GROUP_ORDER			 121
#define FEC_R_INVALID_LEN				 122
#define FEC_R_KEYS_NOT_SET				 150
#define FEC_R_KTI_VERIFY_FAILED				 123
#define FEC_R_MALLOC_FAILED				 124
#define FEC_R_MISSING_PARAMETERS			 125
#define FEC_R_MISSING_PRIVATE_KEY			 126
#define FEC_R_NEW_GROUP_FAILED				 127
#define FEC_R_NON_FIPS_METHOD				 152
#define FEC_R_NO_PARAMETERS_SET				 151
#define FEC_R_NULL_GROUP				 153
#define FEC_R_NULL_GROUP_PASSED_IN			 128
#define FEC_R_NULL_PARMS_PASSED_IN			 129
#define FEC_R_NULL_SIG_PASSED_IN			 130
#define FEC_R_OCT2POINT_FAILED				 131
#define FEC_R_OCT_LEN_FAILED				 132
#define FEC_R_PKPARAMETERS2GROUP_FAILURE		 133
#define FEC_R_POINT2OCT_FAILED				 134
#define FEC_R_POINT_NOT_ON_CURVE			 135
#define FEC_R_P_IS_NOT_PRIME				 136
#define FEC_R_SET_AFFINE_FAILED				 137
#define FEC_R_SET_CURVE_FAILED				 138
#define FEC_R_SLOT_FULL					 144
#define FEC_R_TO_AFFINE_FAILED				 139
#define FEC_R_UNSUPPORTED_FIELDTYPE			 140
#define FEC_R_UNSUPPORTED_FUNCTION			 141

#ifdef  __cplusplus
}
#endif
#endif
