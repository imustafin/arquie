# arquie
Archimate models verification and relationships inference.

## Installation
Gemfile is provided. We suggest using [Bundler](https://bundler.io/). When you have Bundler installed, just run:

```
bundle install
```

## Running
Put Archimate model files into `models` directory then run

```
bundle exec ruby analyze.rb
```

The result of analysis will be in `analysis.json`.
