## [0.5.3](https://github.com/CogniQ/CogniQ/compare/v0.5.2...v0.5.3) (2023-11-13)


### Bug Fixes

* add timezone information to parsed when_time ([ef09ffd](https://github.com/CogniQ/CogniQ/commit/ef09ffd743bb4fd40f74f830a2bb4552b43f5ca9))

## [0.5.2](https://github.com/CogniQ/CogniQ/compare/v0.5.1...v0.5.2) (2023-11-13)


### Bug Fixes

* make more datetimes timezone aware ([c101710](https://github.com/CogniQ/CogniQ/commit/c101710d8c910a6426aebeb5f22366253689c49c))

## [0.5.1](https://github.com/CogniQ/CogniQ/compare/v0.5.0...v0.5.1) (2023-11-13)


### Bug Fixes

* use offset-aware datetime objects ([4df242a](https://github.com/CogniQ/CogniQ/commit/4df242a2d1c2313154fdacd22376c0b1de6cc202))

# [0.5.0](https://github.com/CogniQ/CogniQ/compare/v0.4.26...v0.5.0) (2023-11-13)


### Bug Fixes

* add healthcheck ([cd7d5eb](https://github.com/CogniQ/CogniQ/commit/cd7d5eb0d41e297eb9ffce2ac52794ae371731a1))
* need to check for new tasks more regularly than some far out task ([0c7fccf](https://github.com/CogniQ/CogniQ/commit/0c7fccfec3aa9ca9dbb86e047908342b7cadb8aa))
* pass reply_ts and thread_ts to ask method ([742bd1d](https://github.com/CogniQ/CogniQ/commit/742bd1dbf001ee99c6d8a4018e4cfa458d6a2cb3))
* poetry update 20231113 ([ac42068](https://github.com/CogniQ/CogniQ/commit/ac4206855bdbd8ede50f4240d6e2ced3bf71b5e3))
* thread-ts is a string not a float. ([0636dd0](https://github.com/CogniQ/CogniQ/commit/0636dd0f1d9c8f0df615a11ace5cdb65287dd19d))
* unlock task after faililng to complete ([c74631b](https://github.com/CogniQ/CogniQ/commit/c74631b9987d1fdac3330b440f7b4c889611ee86))


### Features

* add alembic to manage database ([6fe2824](https://github.com/CogniQ/CogniQ/commit/6fe282415c63878da2a25a68ea9be7671f8c1b41))
* enqueue and dequeue tasks ([44cf98d](https://github.com/CogniQ/CogniQ/commit/44cf98d7250f98592ee7a4ef217182ff80b52b06))
* postMessage ([ad280f8](https://github.com/CogniQ/CogniQ/commit/ad280f8709d25e010f0bca0d171a3e1e1bfe0359))

## [0.4.26](https://github.com/CogniQ/CogniQ/compare/v0.4.25...v0.4.26) (2023-09-11)


### Bug Fixes

* permit anthropic claude to stream responses ([165e8cc](https://github.com/CogniQ/CogniQ/commit/165e8cc0eb8dfc1e226a704f4f5b8cc080e0510f))

## [0.4.25](https://github.com/CogniQ/CogniQ/compare/v0.4.24...v0.4.25) (2023-09-11)


### Bug Fixes

* update containerapp to include datadog/serverless-init required env vars ([66666cf](https://github.com/CogniQ/CogniQ/commit/66666cfac9cf48472a03bf00d6dab559816d1623))

## [0.4.24](https://github.com/CogniQ/CogniQ/compare/v0.4.23...v0.4.24) (2023-09-11)


### Bug Fixes

* update deps on 20230910 ([#88](https://github.com/CogniQ/CogniQ/issues/88)) ([26694e9](https://github.com/CogniQ/CogniQ/commit/26694e9ad82b71a3bb4d9d91f4fefba2d7f70dd8))

## [0.4.23](https://github.com/CogniQ/CogniQ/compare/v0.4.22...v0.4.23) (2023-09-07)


### Bug Fixes

* only encapsulate parts of the the code that might raise exceptions in the try block ([e2924b9](https://github.com/CogniQ/CogniQ/commit/e2924b9ecd8c8c338c2570f636b1a13f9aea3fd5))
* unhandled KeyError on delete ([0ff8417](https://github.com/CogniQ/CogniQ/commit/0ff8417531ad628c3cf13f7e4466389fb18480c1))

## [0.4.22](https://github.com/CogniQ/CogniQ/compare/v0.4.21...v0.4.22) (2023-09-07)


### Bug Fixes

* ensure that row exists before attempting to delete it ([54a2473](https://github.com/CogniQ/CogniQ/commit/54a247367b2130e88061f02273cf22b0f21d4634))

## [0.4.21](https://github.com/CogniQ/CogniQ/compare/v0.4.20...v0.4.21) (2023-09-05)


### Bug Fixes

* use config as a module.  ([#83](https://github.com/CogniQ/CogniQ/issues/83)) ([2e47c22](https://github.com/CogniQ/CogniQ/commit/2e47c22ba0c0fe4846637bbc758aa52a5f15fac2))

## [0.4.20](https://github.com/CogniQ/CogniQ/compare/v0.4.19...v0.4.20) (2023-09-04)


### Bug Fixes

* constrained cpu / memory combinations: ([c399914](https://github.com/CogniQ/CogniQ/commit/c399914fafbb9208f2daa9e80431897d1898de87))
* historical usage indicates we do not need as much cpu as we thought ([2c313c7](https://github.com/CogniQ/CogniQ/commit/2c313c70950f7f71fae8e0ab461ef6149ddf31c3))

## [0.4.19](https://github.com/CogniQ/CogniQ/compare/v0.4.18...v0.4.19) (2023-07-17)


### Bug Fixes

* perform an upsert when possible ([#77](https://github.com/CogniQ/CogniQ/issues/77)) ([0813648](https://github.com/CogniQ/CogniQ/commit/08136481fe8c4b6610570671f8c880b4d8726599))

## [0.4.18](https://github.com/CogniQ/CogniQ/compare/v0.4.17...v0.4.18) (2023-07-17)


### Bug Fixes

* perform an upsert when possible ([5b14e0b](https://github.com/CogniQ/CogniQ/commit/5b14e0bc6effe41cf81669bf67ff7f5db651188e))

## [0.4.17](https://github.com/CogniQ/CogniQ/compare/v0.4.16...v0.4.17) (2023-07-16)


### Bug Fixes

* The 'warn' method is deprecated, use 'warning' instead ([7ced2ea](https://github.com/CogniQ/CogniQ/commit/7ced2ea9032ba7e49209ad55e7747e2c4dcc7c82))

## [0.4.16](https://github.com/CogniQ/CogniQ/compare/v0.4.15...v0.4.16) (2023-07-16)


### Bug Fixes

* adds psql utility command to image ([47c3bb5](https://github.com/CogniQ/CogniQ/commit/47c3bb5c0c2eeda2096d2775339f69b93507338b))

## [0.4.15](https://github.com/CogniQ/CogniQ/compare/v0.4.14...v0.4.15) (2023-07-16)


### Bug Fixes

* InstallationStore was not correctly finding the installation with the user's token. ([#76](https://github.com/CogniQ/CogniQ/issues/76)) ([a9ba383](https://github.com/CogniQ/CogniQ/commit/a9ba38357b37b096cf6454abd588c35fc3fc2e13))

## [0.4.14](https://github.com/CogniQ/CogniQ/compare/v0.4.13...v0.4.14) (2023-06-27)


### Bug Fixes

* handle the case where the personality has an unhandled error ([eba7bcc](https://github.com/CogniQ/CogniQ/commit/eba7bcce3412827821762bef61f9d7b4d7519ebf))
* lol maybe the workflow named `on_pull_request` should fire on pull_request ([4af8404](https://github.com/CogniQ/CogniQ/commit/4af84044a932399e404f54433061a6dd29bb811e))
* return error when personality fails ([2b5dd0b](https://github.com/CogniQ/CogniQ/commit/2b5dd0baf6c422031a628b97ab5203215c2b14af))

## [0.4.13](https://github.com/CogniQ/CogniQ/compare/v0.4.12...v0.4.13) (2023-06-27)


### Bug Fixes

* enable log collection ([96de6fd](https://github.com/CogniQ/CogniQ/commit/96de6fd81cbbeb12a030a04a4ac7aac6c498c111))
* remove a syntax error in the deployment manifest ([ac29555](https://github.com/CogniQ/CogniQ/commit/ac295559f0357bf98edc07b1aedaa062b59f5b1e))
* rotate tokens upon expiry ([#74](https://github.com/CogniQ/CogniQ/issues/74)) ([3a31697](https://github.com/CogniQ/CogniQ/commit/3a31697651e5e76fe1371d188706e3165599bc7f)), closes [#72](https://github.com/CogniQ/CogniQ/issues/72)
* trigger deploy since i mistakenly had a skip token in the previous commit ([4606f38](https://github.com/CogniQ/CogniQ/commit/4606f38c8126254ad3feda91f0112837dfb19474))

## [0.4.12](https://github.com/CogniQ/CogniQ/compare/v0.4.11...v0.4.12) (2023-06-26)


### Bug Fixes

* the action needs space delimited to define env vars ([58e4406](https://github.com/CogniQ/CogniQ/commit/58e4406ff12ac7110dde30f126dedaa3fde1b4cb))

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
