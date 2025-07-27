---
layout: default
title: Getting Started
nav_order: 1
permalink: /getting-started/
---

# Getting Started

Welcome to the Respondua documentation! This guide will help you set up the project locally and understand its structure.

## Requirements

- Docker + Docker Compose
- Node.js + Yarn
- Python 3.x + pip

## Setup

```bash
git clone https://github.com/your-org/respondua
cd respondua
docker-compose up
```

```bash
brew install chruby ruby-install

ruby-install ruby 3.1.2

echo "source $(brew --prefix)/opt/chruby/share/chruby/chruby.sh" >> ~/.zshrc
echo "source $(brew --prefix)/opt/chruby/share/chruby/auto.sh" >> ~/.zshrc
echo "chruby ruby-3.1.2" >> ~/.zshrc # run 'chruby' to see actual version

source ~/.zshrc 

ruby -v                         
ruby 3.1.2p20 (2022-04-12 revision 4491bb740a) [arm64-darwin24]

bundle install

bundle exec jekyll serve
```