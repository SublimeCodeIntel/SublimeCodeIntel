/**
 * Use require('crypto') to access this module.
 */
var crypto = {};

crypto.Hash = function() {}
crypto.Hash.prototype = {}
/**
 * Updates the hash content with the given data. This can be called many
 * times with new data as it is streamed.
 */
crypto.Hash.prototype.update = function() {}
/**
 * Calculates the digest of all of the passed data to be hashed. The
 * encoding can be 'hex', 'binary' or 'base64'.
 */
crypto.Hash.prototype.digest = function() {}

/**
 * Creates and returns a cipher object, with the given algorithm and key.
 * @returns Cipher
 */
crypto.createCipher = function() {}

/**
 * Creates and returns a hmac object, a cryptographic hmac with the given
 * algorithm and key.
 * @returns Hmac
 */
crypto.createHmac = function() {}

crypto.Verify = function() {}
crypto.Verify.prototype = {}
/**
 * Verifies the signed data by using the cert which is a string containing
 * the PEM encoded certificate, and signature, which is the previously
 * calculates signature for the data, in the signature_format which can be
 * 'binary', 'hex' or 'base64'.
 */
crypto.Verify.prototype.verify = function() {}
/**
 * Updates the verifier object with data. This can be called many times
 * with new data as it is streamed.
 */
crypto.Verify.prototype.update = function() {}

/**
 * Creates a credentials object, with the optional details being a
 * dictionary with keys:
 */
crypto.createCredentials = function() {}

/**
 * Creates and returns a signing object, with the given algorithm. On
 * recent OpenSSL releases, openssl list-public-key-algorithms will display
 * the available signing algorithms. Examples are 'RSA-SHA256'.
 * @returns Sign
 */
crypto.createSign = function() {}

crypto.Sign = function() {}
crypto.Sign.prototype = {}
/**
 * Updates the signer object with data. This can be called many times with
 * new data as it is streamed.
 */
crypto.Sign.prototype.update = function() {}
/**
 * Calculates the signature on all the updated data passed through the
 * signer. private_key is a string containing the PEM encoded private key
 * for signing.
 */
crypto.Sign.prototype.sign = function() {}

crypto.Cipher = function() {}
crypto.Cipher.prototype = {}
/**
 * Updates the cipher with data, the encoding of which is given in
 * input_encoding and can be 'utf8', 'ascii' or 'binary'. The
 * output_encoding specifies the output format of the enciphered data, and
 * can be 'binary', 'base64' or 'hex'.
 */
crypto.Cipher.prototype.update = function() {}
/**
 * Returns any remaining enciphered contents, with output_encoding being
 * one of: 'binary', 'ascii' or 'utf8'.
 */
crypto.Cipher.prototype.final = function() {}

/**
 * Creates and returns a hash object, a cryptographic hash with the given
 * algorithm which can be used to generate hash digests.
 * @returns Hash
 */
crypto.createHash = function() {}

crypto.Decipher = function() {}
crypto.Decipher.prototype = {}
/**
 * Updates the decipher with data, which is encoded in 'binary', 'base64'
 * or 'hex'. The output_decoding specifies in what format to return the
 * deciphered plaintext: 'binary', 'ascii' or 'utf8'.
 */
crypto.Decipher.prototype.update = function() {}
/**
 * Returns any remaining plaintext which is deciphered, with
 * output_encoding' being one of: 'binary', 'ascii' or 'utf8'`.
 */
crypto.Decipher.prototype.final = function() {}

crypto.Credentials = function() {}
crypto.Credentials.prototype = {}

/**
 * Creates and returns a decipher object, with the given algorithm and key.
 * This is the mirror of the cipher object above.
 * @returns Decipher
 */
crypto.createDecipher = function() {}

/**
 * Creates and returns a verification object, with the given algorithm.
 * This is the mirror of the signing object above.
 * @returns Verify
 */
crypto.createVerify = function() {}

crypto.Hmac = function() {}
crypto.Hmac.prototype = {}
/**
 * Update the hmac content with the given data. This can be called many
 * times with new data as it is streamed.
 */
crypto.Hmac.prototype.update = function() {}
/**
 * Calculates the digest of all of the passed data to the hmac. The
 * encoding can be 'hex', 'binary' or 'base64'.
 */
crypto.Hmac.prototype.digest = function() {}


exports = crypto;

