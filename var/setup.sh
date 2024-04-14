#!/usr/bin/env bash

set -e

export GEM_HOME=$HOME/gems
export PATH=$HOME/gems/bin:$PATH

echo "GEM_HOME=$GEM_HOME" >> $GITHUB_ENV
echo "PATH=$PATH" >> $GITHUB_ENV

node --version
npm --version
gem install jekyll bundler
bundle install
