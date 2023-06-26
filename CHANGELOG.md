## [0.4.11](https://github.com/CogniQ/CogniQ/compare/v0.4.10...v0.4.11) (2023-06-26)


### Bug Fixes

* the troubles i go to to have DD_VERSION working ([a31828a](https://github.com/CogniQ/CogniQ/commit/a31828afbd4ffb4329d9080464faeae984e40b64))

## [0.4.10](https://github.com/CogniQ/CogniQ/compare/v0.4.9...v0.4.10) (2023-06-26)


### Bug Fixes

* distinguish between sha for container and tag for the DD_VERSION ([59c79da](https://github.com/CogniQ/CogniQ/commit/59c79da27dd132334cb31570d2b9d0eb11fec8f6))

## [0.4.9](https://github.com/CogniQ/CogniQ/compare/v0.4.8...v0.4.9) (2023-06-26)


### Bug Fixes

* add ddtrace agent ([#73](https://github.com/CogniQ/CogniQ/issues/73)) ([7ad86e1](https://github.com/CogniQ/CogniQ/commit/7ad86e1fdedbaa57d140638fd40e2e5af88146d3))
* set a generous timeout in case a personality crashes ([1f4012d](https://github.com/CogniQ/CogniQ/commit/1f4012d3f1fdd5e11821373fd222a22761d681ae))

## [0.4.8](https://github.com/CogniQ/CogniQ/compare/v0.4.7...v0.4.8) (2023-06-26)


### Bug Fixes

* docker metadata outputs 7 chars for short sha ([acc72bd](https://github.com/CogniQ/CogniQ/commit/acc72bd611b17cf44ceead100aaa649176255e21))

## [0.4.7](https://github.com/CogniQ/CogniQ/compare/v0.4.6...v0.4.7) (2023-06-26)


### Bug Fixes

* remove GPU dependency for devcontainer and poetry.lock ([b6778b4](https://github.com/CogniQ/CogniQ/commit/b6778b48a3da5814ad9c8687c8d0e2db169b6924))
* when deploying to cogniq-community-main, always specify short sha of container image ([24ca540](https://github.com/CogniQ/CogniQ/commit/24ca5402752348e29ceafad3c52bb9a91106d45c))

## [0.4.6](https://github.com/CogniQ/CogniQ/compare/v0.4.5...v0.4.6) (2023-06-20)


### Bug Fixes

* downgrade the docker image to the cpu version ([f70c619](https://github.com/CogniQ/CogniQ/commit/f70c619de942e8287282dde6cfc549b501d30099)), closes [#63](https://github.com/CogniQ/CogniQ/issues/63)

## [0.4.5](https://github.com/CogniQ/CogniQ/compare/v0.4.4...v0.4.5) (2023-06-20)


### Bug Fixes

* do not stream the final response, as it bleeds into the first round of results ([64bd197](https://github.com/CogniQ/CogniQ/commit/64bd197dc714465eedd968be1bf45f01c08ba30c))

## [0.4.4](https://github.com/CogniQ/CogniQ/compare/v0.4.3...v0.4.4) (2023-06-20)


### Bug Fixes

* **deps:** update haystack to 1.17.2 ([8d0e526](https://github.com/CogniQ/CogniQ/commit/8d0e526caf4b8f56858249e9cb0e72c30c6ae4dc))

## [0.4.3](https://github.com/CogniQ/CogniQ/compare/v0.4.2...v0.4.3) (2023-06-20)


### Bug Fixes

* feed semver to build step ([aeb389a](https://github.com/CogniQ/CogniQ/commit/aeb389a2c1e0f7ecdcf8f4256dd2adb772377412))
* ignore .github directory when building ([6554ac0](https://github.com/CogniQ/CogniQ/commit/6554ac0691a5cf7020cedc6178c01b4900952cd9))

## [0.4.2](https://github.com/CogniQ/CogniQ/compare/v0.4.1...v0.4.2) (2023-06-20)


### Bug Fixes

* fix docker image tagging ([5b2e50c](https://github.com/CogniQ/CogniQ/commit/5b2e50c3fc7a29250969aa04932a0a7c1b23ce7c))

## [0.4.1](https://github.com/CogniQ/CogniQ/compare/v0.4.0...v0.4.1) (2023-06-20)


### Bug Fixes

* really cut down on the slack search personality's... personality. ([683fe45](https://github.com/CogniQ/CogniQ/commit/683fe458495bd7746d68d0a27dffd9e064ba1205))
* reduce the amount of interpretation that slack_search personality performs ([7022d32](https://github.com/CogniQ/CogniQ/commit/7022d322ad5da3dd8bc7c724b63207eb1eb40e93))
* release using semantic release ([38b6e75](https://github.com/CogniQ/CogniQ/commit/38b6e75454db0d8e1908125960a0a71880d22c91))
* remove gha cache scoping ([e70e054](https://github.com/CogniQ/CogniQ/commit/e70e05456981b1773e5469904c51bece4bce5f8e))
* slack history should ignore the current conversation ([ecab8c9](https://github.com/CogniQ/CogniQ/commit/ecab8c95d452b9c958b5ce984d28a10ce4c6270d))
* trim from the end of the list, given search responses are time descending ([174549f](https://github.com/CogniQ/CogniQ/commit/174549f2027a66107699bd1db29c252ba74023f3))
