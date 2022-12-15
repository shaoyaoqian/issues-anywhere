require 'openssl'
require 'jwt'  # https://rubygems.org/gems/jwt

# Private key contents
private_pem = File.read("wechat-to-issues.2022-12-14.private-key.pem")
private_key = OpenSSL::PKey::RSA.new(private_pem)

puts Time.now.to_i
puts private_key

# Generate the JWT
payload = {
  # issued at time, 60 seconds in the past to allow for clock drift
#   iat: 1671082469 - 60,
  iat: Time.now.to_i - 60,
  # JWT expiration time (10 minute maximum)
  exp: Time.now.to_i + (10 * 60),
  # GitHub App's identifier
  iss: "272667"
}

jwt = JWT.encode(payload, private_key, "RS256")
puts jwt