/**
 * Use require('crypto') to access this module.
 */
var crypto = {};

/**
 * The class for creating hash digests of data.
 * @constructor
 */
crypto.Hash = function() {}

/**
 * Updates the hash content with the given data, the encoding of which is
 * given in input_encoding and can be 'utf8', 'ascii' or 'binary'.
 * @param data
 * @param input_encoding
 */
crypto.Hash.prototype.update = function(data, input_encoding) {}

/**
 * Calculates the digest of all of the passed data to be hashed.
 * @param encoding
 */
crypto.Hash.prototype.digest = function(encoding) {}

/**
 * Creates and returns a cipher object, with the given algorithm and
 * password.
 * @param algorithm
 * @param password
 * @returns {crypto.Cipher}
 */
crypto.createCipher = function(algorithm, password) {}

/**
 * Creates and returns a hmac object, a cryptographic hmac with the given
 * algorithm and key.
 * @param algorithm
 * @param key
 * @returns {crypto.Hmac}
 */
crypto.createHmac = function(algorithm, key) {}

/**
 * Class for verifying signatures.
 * @constructor
 */
crypto.Verify = function() {}

/**
 * Verifies the signed data by using the object and signature. object is a
 * string containing a PEM encoded object, which can be one of RSA public
 * key, DSA public key, or X.509 certificate. signature is the previously
 * calculated signature for the data, in the signature_format which can be
 * 'binary', 'hex' or 'base64'. Defaults to 'binary'.
 * @param object
 * @param signature
 * @param signature_format='binary' {String}
 */
crypto.Verify.prototype.verify = function(object, signature, signature_format) {}

/**
 * Updates the verifier object with data.
 * @param data
 */
crypto.Verify.prototype.update = function(data) {}

/**
 * Creates a credentials object, with the optional details being a
 * dictionary with keys:
 * @param details
 * @returns a credentials object, with the optional details being a dictionary with keys:
 */
crypto.createCredentials = function(details) {}

/**
 * Creates and returns a signing object, with the given algorithm.
 * @param algorithm
 * @returns {crypto.Signer}
 */
crypto.createSign = function(algorithm) {}

/**
 * Class for generating signatures.
 * @constructor
 */
crypto.Signer = function() {}

/**
 * Updates the signer object with data.
 * @param data
 */
crypto.Signer.prototype.update = function(data) {}

/**
 * Calculates the signature on all the updated data passed through the
 * signer.
 * @param private_key
 * @param output_format
 */
crypto.Signer.prototype.sign = function(private_key, output_format) {}

/**
 * Class for encrypting data.
 * @constructor
 */
crypto.Cipher = function() {}

/**
 * Updates the cipher with data, the encoding of which is given in
 * input_encoding and can be 'utf8', 'ascii' or 'binary'.
 * @param data
 * @param input_encoding
 * @param output_encoding
 */
crypto.Cipher.prototype.update = function(data, input_encoding, output_encoding) {}

/**
 * Returns any remaining enciphered contents, with output_encoding being
 * one of:
 * @param output_encoding
 * @returns any remaining enciphered contents, with output_encoding being one of:
 */
crypto.Cipher.prototype.final = function(output_encoding) {}

/**
 * Creates and returns a hash object, a cryptographic hash with the given
 * algorithm which can be used to generate hash digests.
 * @param algorithm
 * @returns {crypto.Hash}
 */
crypto.createHash = function(algorithm) {}

/**
 * Class for decrypting data.
 * @constructor
 */
crypto.Decipher = function() {}

/**
 * Updates the decipher with data, which is encoded in 'binary', 'base64'
 * or 'hex'. Defaults to 'binary'.
 * @param data
 * @param input_encoding='binary' {String}
 * @param output_encoding='binary' {String}
 */
crypto.Decipher.prototype.update = function(data, input_encoding, output_encoding) {}

/**
 * Returns any remaining plaintext which is deciphered, with
 * output_encoding being one of: 'binary', 'ascii' or 'utf8'.
 * @param output_encoding
 * @returns any remaining plaintext which is deciphered, with output_encoding being one of: 'binary', 'ascii' or 'utf8'
 */
crypto.Decipher.prototype.final = function(output_encoding) {}

/**
 * Creates and returns a decipher object, with the given algorithm and key.
 * @param algorithm
 * @param password
 * @returns {crypto.Decipher}
 */
crypto.createDecipher = function(algorithm, password) {}

/**
 * Creates and returns a verification object, with the given algorithm.
 * @param algorithm
 * @returns {crypto.Verify}
 */
crypto.createVerify = function(algorithm) {}

/**
 * Class for creating cryptographic hmac content.
 * @constructor
 */
crypto.Hmac = function() {}

/**
 * Update the hmac content with the given data.
 * @param data
 */
crypto.Hmac.prototype.update = function(data) {}

/**
 * Calculates the digest of all of the passed data to the hmac.
 * @param encoding
 */
crypto.Hmac.prototype.digest = function(encoding) {}

/**
 * Creates and returns a cipher object, with the given algorithm, key and
 * iv.
 * @param algorithm
 * @param key
 * @param iv
 * @returns {crypto.Cipher}
 */
crypto.createCipheriv = function(algorithm, key, iv) {}

/**
 * Creates and returns a decipher object, with the given algorithm, key and
 * iv.
 * @param algorithm
 * @param key
 * @param iv
 * @returns {crypto.Decipher}
 */
crypto.createDecipheriv = function(algorithm, key, iv) {}

/**
 * Creates a Diffie-Hellman key exchange object and generates a prime of
 * the given bit length. The generator used is 2.
 * @param prime_length
 * @returns {crypto.DiffieHellman}
 */
crypto.createDiffieHellman = function(prime_length) {}

/**
 * Creates a Diffie-Hellman key exchange object using the supplied prime.
 * The generator used is 2. Encoding can be 'binary', 'hex', or 'base64'.
 * @param prime
 * @param encoding
 * @returns {crypto.DiffieHellman}
 */
crypto.createDiffieHellman = function(prime, encoding) {}

/**
 * The class for creating Diffie-Hellman key exchanges.
 * @constructor
 */
crypto.DiffieHellman = function() {}

/**
 * Generates private and public Diffie-Hellman key values, and returns the
 * public key in the specified encoding. This key should be transferred to
 * the other party. Encoding can be 'binary', 'hex', or 'base64'.
 * @param encoding
 */
crypto.DiffieHellman.prototype.generateKeys = function(encoding) {}

/**
 * Computes the shared secret using other_public_key as the other party's
 * public key and returns the computed shared secret. Supplied key is
 * interpreted using specified input_encoding, and secret is encoded using
 * specified output_encoding. Encodings can be 'binary', 'hex', or
 * 'base64'. The input encoding defaults to 'binary'.
 * @param other_public_key
 * @param input_encoding='binary' {String}
 * @param output_encoding
 */
crypto.DiffieHellman.prototype.computeSecret = function(other_public_key, input_encoding, output_encoding) {}

/**
 * Returns the Diffie-Hellman prime in the specified encoding, which can be
 * 'binary', 'hex', or 'base64'. Defaults to 'binary'.
 * @param encoding='binary' {String}
 * @returns the Diffie-Hellman prime in the specified encoding, which can be 'binary', 'hex', or 'base64'
 */
crypto.DiffieHellman.prototype.getPrime = function(encoding) {}

/**
 * Returns the Diffie-Hellman prime in the specified encoding, which can be
 * 'binary', 'hex', or 'base64'. Defaults to 'binary'.
 * @param encoding='binary' {String}
 * @returns the Diffie-Hellman prime in the specified encoding, which can be 'binary', 'hex', or 'base64'
 */
crypto.DiffieHellman.prototype.getGenerator = function(encoding) {}

/**
 * Returns the Diffie-Hellman public key in the specified encoding, which
 * can be 'binary', 'hex', or 'base64'. Defaults to 'binary'.
 * @param encoding='binary' {String}
 * @returns the Diffie-Hellman public key in the specified encoding, which can be 'binary', 'hex', or 'base64'
 */
crypto.DiffieHellman.prototype.getPublicKey = function(encoding) {}

/**
 * Returns the Diffie-Hellman private key in the specified encoding, which
 * can be 'binary', 'hex', or 'base64'. Defaults to 'binary'.
 * @param encoding='binary' {String}
 * @returns the Diffie-Hellman private key in the specified encoding, which can be 'binary', 'hex', or 'base64'
 */
crypto.DiffieHellman.prototype.getPrivateKey = function(encoding) {}

/**
 * Sets the Diffie-Hellman public key. Key encoding can be 'binary', 'hex',
 * or 'base64'. Defaults to 'binary'.
 * @param public_key
 * @param encoding='binary' {String}
 */
crypto.DiffieHellman.prototype.setPublicKey = function(public_key, encoding) {}

/**
 * Sets the Diffie-Hellman private key. Key encoding can be 'binary',
 * 'hex', or 'base64'. Defaults to 'binary'.
 * @param public_key
 * @param encoding='binary' {String}
 */
crypto.DiffieHellman.prototype.setPrivateKey = function(public_key, encoding) {}

/**
 * Asynchronous PBKDF2 applies pseudorandom function HMAC-SHA1 to derive a
 * key of given length from the given password, salt and iterations.
 * @param password
 * @param salt
 * @param iterations
 * @param keylen
 * @param callback
 */
crypto.pbkdf2 = function(password, salt, iterations, keylen, callback) {}

/**
 * Generates cryptographically strong pseudo-random data. Usage:
 * @param size
 * @param callback
 */
crypto.randomBytes = function(size, callback) {}

exports = crypto;

