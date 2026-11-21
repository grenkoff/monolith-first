# Changelog

Every release of this project, built by `make changelog` from Conventional Commits.

## v2026.11.21

### Features

- **commit-lint**: Check headers, types, scopes and the one-line rule
- **clones**: Find blocks of eight lines repeated in python and rust code
- **hooks**: Refuse implementation edits until a test fails
- **catalog**: Render the home and product pages in one layout
- **orders**: Place orders from the product page and show the order
- **core**: Style every page with one design system and three themes
- **catalog**: Rank names by the resemblance of their words in rust
- **catalog**: Search products by name, ranked in rust
- **core**: Render the theme switcher and the live total for web components
- **core**: Add the theme switcher and live total components
- **proto**: Add the contract of the images service
- **images**: Fit photos to a width and draw them as thumbnails
- **images**: Serve thumbnails over grpc with a health check
- **catalog**: Add the table of product thumbnails
- **catalog**: Keep thumbnails of product photos made by the images service
- **catalog**: Show product thumbnails in the admin
- **hooks**: Create a module of core with every layer and install it

### Bug fixes

- **catalog**: Keep the docstring of the home page out of the pattern registry
- **core**: Read whole answers in the end-to-end check before matching them
- **core**: Judge contrast to two decimals and channels by their eight-bit value
- **core**: Restore the executable bit of the ci and doctor scripts
- **images**: Keep the fitted height within the height of the photo
- **catalog**: Accept photos up to 8 MB in requests up to 12 MB
- **hooks**: Drop the executable bit of the generator and its docs

### Refactoring

- **core**: Name the namespaces of page routes in the root config
- **core**: Serve the design page as a template view
- **core**: Declare the design page in the routes without a view class
- **hooks**: Read the technical names from the module check

### Documentation

- **agents**: Set the rules of a web template with python and rust
- **readme**: Rename the template to monolith-first
- **agents**: Describe the tooling without node.js
- Describe the pages and the stylesheet build
- Describe the tokens, themes, components and checks of the design system
- Describe rust inside the monolith and the catalog search
- Describe web components, Biome and the browser tests
- Describe the images service as the example of an extracted service
- Start a new product with /new-product and the questionnaire
- List every part of the example to remove for a new product

### Build

- **tools**: Run commit-lint, clones and the tdd hook instead of node tools
- Remove node.js, npm and their lock files from the tooling
- **core**: Build the stylesheet with the tailwind standalone cli
- **core**: Check, cover and mutate the rust extension module with the workspace
- **images**: Run the images service in compose next to core
- **core**: Add grpc, the generated images contract and its settings
- **core**: Keep the rust build folder out of the spelling checks
- Add make module to create a module of core

## v2026.11.19

### Features

- **core**: Report a call chain between modules
- **core**: Report modules named after a technical layer
- **core**: Report model relations between modules
- **core**: Report a call to another module inside a transaction
- **core**: Report compose services that face the world or share a database
- **eo-lint**: Reject grpc clients in services
- **core**: Report models without a uuid7 primary key
- **main**: Give blog posts uuid7 ids
- **accounts**: Give users uuid7 ids in their own model
- **catalog**: Keep products with uuid7 ids in the catalog
- **catalog**: Show products by id behind the catalog facade
- **catalog**: Accept only visible names and prices up to a million
- **orders**: Total an order from the current price of its product
- **orders**: Place orders through the catalog facade
- **orders**: Answer 409 for products not on sale and limit quantities
- **orders**: Show orders by id
- **core**: Count a subscription to the events of a module as no call
- **orders**: Write an order placed event to the outbox with the order
- **core**: Relay the oldest pending outbox event to its subscribers
- **catalog**: Record each placed order as a sale of its product
- **core**: Relay outbox events in a command that drains the outbox on sigterm
- **core**: Poll the relay and wait only while no event is pending
- **core**: **breaking**: Remove the hello example service and its greetings client

### Bug fixes

- **core**: Accept relations from framework models to modules
- **core**: Read whole floats in request bodies as integers
- **catalog**: Record a sale once however often its event is delivered

### Refactoring

- **core**: Share the reading of import statements between the checks
- **core**: Build module objects in the composition root by hand
- **core**: Share the pattern of visible text between modules
- **core**: Remove the main example with its migration-linter exceptions
- **core**: Build the catalog facade once and hand it to orders
- **core**: Wire each module in a file of its own under the composition root
- **core**: Run the relay command on the polling loop

### Dependencies

- **deps**: Bump python from 3.14.9 to 3.14.10 (#49)
- **deps**: Bump prost from 0.14.4 to 0.14.6 and syn from 3.0.9 to 3.0.10 (#51)

### Documentation

- Make the template a modular monolith that extracts services when needed
- Make the public package the innermost layer of a module
- Describe the checks that keep out the distributed monolith
- Name the user model and the check of uuid7 primary keys
- Describe catalog and orders as the example of modules
- Register the catalog facade and its adapter in the patterns registry
- Describe the outbox, its relay and the composition of modules
- Register the sales observer in the patterns registry
- Describe the monolith without the example service
- Add the recipe that extracts a module by strangler fig

### Build

- **core**: Let the infra of a module import only the public package of another
- **core**: Let ruff read the model _meta api of django
- Pin the generators of the python contracts to exact versions
- Run the outbox relay in compose and check it end to end
- **contracts**: Generate code for every contract in proto
- **proto**: Skip buf and code generation when proto holds no contract
- Separate the releases of the changelog with a blank line

### CI

- Check in its own job that no distributed monolith appears
- Check uuid7 primary keys with the architecture
- Allow listed npm advisories that have no fix and never reach the system
- Drop the picomatch advisory that npm audit no longer reports

## v2026.11.14

### Features

- Add polyglot backend template
- **core**: Report no problems for documented modules
- **core**: Report functions and classes without docstrings
- **core**: Report multi-line docstrings
- **core**: Report modules without docstrings
- **core**: Skip empty modules in the docstring check
- **core**: Skip test functions in the docstring check
- **core**: Check every module under a directory except excluded paths
- **eo-lint**: Report docs of more than one line as EO012
- **eo-lint**: Report each long doc once and keep module and item docs apart
- **greetings**: Record every event an inbox delivers
- **greetings**: Receive greeting events from nats
- **greetings**: Record greeting events until sigterm drains nats
- **greetings**: Fail fast when nats is unreachable and let compose restart the listener
- **eo-lint**: Report i/o crates imported by domain modules as EO010
- **eo-lint**: Report full paths to i/o crates in domain modules
- **eo-lint**: Report outer layers imported by domain modules
- **hello**: Translate the domain greeted event into protobuf for nats
- **eo-lint**: Report grouped and renamed imports in domain modules
- **core**: Report grpc calls inside atomic transactions
- **core**: Report network calls inside an imported atomic
- **core**: Report network calls in functions decorated as atomic
- **core**: Leave calls deferred to on_commit out of the transaction check
- **core**: Check every module of the server for network calls in transactions
- **eo-lint**: Report awaits inside transactions as EO011
- **eo-lint**: Accept awaits that use the open transaction
- **eo-lint**: List rust items that name a pattern
- **eo-lint**: List python classes and modules that name a pattern
- **eo-lint**: Reject pattern names outside the allowed list
- **eo-lint**: Collect the sorted registry of a directory
- **eo-lint**: Leave generated and test code out of the registry
- **eo-lint**: Render the registry as a markdown table
- **eo-lint**: Print the registry of patterns with the patterns binary
- **core**: Give up on a database lock after 5 seconds
- **eo-lint**: List rust enums that name a pattern
- **eo-lint**: List rust traits that name a pattern
- **eo-lint**: List rust modules whose documentation names a pattern

### Bug fixes

- **greetings**: Require a non-whitespace character in names
- **greetings**: Close the nats client when connecting times out
- **eo-lint**: Stop honouring cfg_attr waivers
- **greetings**: Spell out unicode whitespace in the name pattern

### Refactoring

- **greetings**: Drop the unreachable blank name response
- **core**: Split docstring reports into small objects with an entry point
- **eo-lint**: Track doc lines with a small value object
- **greetings**: Bound the nats flush by the timeout setting
- **greetings**: Move nats test helpers into a pytest plugin
- **greetings**: Drop the coverage pragma from the error fallback
- **greetings**: Run the nats listener as an object with an injected journal
- **greetings**: Name the fail-fast connection option
- **eo-lint**: Build every EO010 finding from one intrusion object
- **hello**: Move names, greetings and events into the domain layer
- **hello**: Move the nats adapter and settings into the infra layer
- **hello**: Move the grpc endpoint and health check into the api layer
- **core**: Match calls and transactions by their source text
- **greetings**: Trim the same whitespace in the fake hello service
- **eo-lint**: Write the heading of the registry in one piece
- **core**: Declare the protocols that the check scripts implement
- **eo-lint**: Share one code object between the linter and the registry
- **core**: Take the database timeouts from settings
- **eo-lint**: Build every rust claim from its documentation

### Dependencies

- **deps**: Bump astral-sh/setup-uv from 6 to 7 (#3)
- **deps**: Bump actions/checkout from 5 to 7 (#1)
- **deps**: Bump actions/setup-node from 5 to 7 (#4)
- **deps**: Bump python from 3.14.8 to 3.14.9 (#6)
- **deps**: Bump syn from 2.0.119 to 3.0.9 (#5)
- **deps**: Bump filelock and certifi to fixed versions
- **deps**: Bump opentelemetry-api from 1.45.1 to 1.45.2
- **deps**: Bump dnspython from 2.9.0 to 2.9.2

### Documentation

- Describe how to land bot pull requests
- Rewrite agent rules (#7)
- Describe the contracts crate
- **core**: Give every module, class and function a one-line docstring
- **eo-lint**: Document every item in one line
- **hello**: Document every item in one line
- Note that core integration tests use a real nats
- State that elegant objects rules have no exceptions
- Describe the layers of rust services and EO010 on contracts
- Point to the transaction check of core and what it allows
- Describe the names that vulture and cargo-machete ignore
- Describe what cargo-deny blocks and what it reports
- Describe the developer setup with make doctor and make setup
- Describe the coverage gates of domain logic and the rest
- Say where the lock and statement timeouts of migrations are set
- Describe make changelog and make release-notes in the release steps
- **core**: Point to the changelog of the repository root
- Add the cookbook of typical tasks
- Describe make contracts and the buf checks of make proto
- Take every dependency of a new rust service from the workspace
- List the rust items whose documentation may name a pattern

### Build

- **contracts**: Generate rust code from proto in its own crate
- **core**: Require one-line docstrings in ruff and ci
- Deny missing docs in every hand-written rust crate
- **core**: Run nats next to the core tests with a connect timeout setting
- Stop declaring the eo cfg
- **core**: Set the python line length to 88
- Generate docs/patterns.md with make patterns
- Deny unused code in every rust crate
- Pin node 26 in .nvmrc and use it in ci
- Add make doctor and make setup
- Write the changelog with git-cliff in make changelog
- Format every file the agent writes with ruff or rustfmt
- Suggest make setup when the probity hook is off
- Add the patterns and cookbook commands and the pattern-reviewer subagent
- Check contracts with buf in make proto and add make contracts
- **hello**: Take every dependency from the workspace
- **hello**: Drop the comments and directives from the dockerfile
- Title each changelog release by its calendar version alone

### CI

- Disable buf pull request comments
- Skip minor python image updates in dependabot
- Run on develop and production branches
- Install protoc from github releases instead of apt
- Run core checks as the host user through make targets
- **core**: Run the transaction check with the linters
- Fail when docs/patterns.md is out of date
- Find unused rust dependencies with cargo-machete
- **core**: Find dead python code with vulture
- **core**: Fail the pipeline on vulnerable python dependencies
- Check secrets, rust and npm dependencies with gitleaks, cargo-deny and npm audit
- Reject duplicated python and rust code with jscpd
- **rust**: Require full line coverage in src/domain and 80% overall
- **core**: Require full coverage in logic and 80% overall
- Run make contracts in the contracts job
