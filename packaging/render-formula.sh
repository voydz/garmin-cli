#!/usr/bin/env bash
# Render the Homebrew formula for a multi-platform release.
#
# `brew bump-formula-pr` only understands a formula with a single top-level
# url/sha256 pair, so the release workflow renders the whole formula instead.
#
# Required environment:
#   VERSION            release version without the leading "v" (e.g. 0.3.0)
#   TAG                git tag of the release (e.g. v0.3.0)
#   SHA256_MACOS_ARM64
#   SHA256_MACOS_X86_64
#   SHA256_LINUX_X86_64
#   SHA256_LINUX_AARCH64
#
# Every os/arch combination Homebrew evaluates needs a URL: `brew readall
# --os=all --arch=all` fails the tap with "formula requires at least a URL"
# if any block is missing. No `version` stanza either — Homebrew scans it
# from the URL and audit rejects it as redundant.
set -euo pipefail

: "${VERSION:?}" "${TAG:?}"
: "${SHA256_MACOS_ARM64:?}" "${SHA256_MACOS_X86_64:?}"
: "${SHA256_LINUX_X86_64:?}" "${SHA256_LINUX_AARCH64:?}"

base="https://github.com/voydz/garmin-cli/releases/download/${TAG}"

cat <<FORMULA
class GarminCli < Formula
  desc "CLI for reading health data from Garmin Connect"
  homepage "https://github.com/voydz/garmin-cli"

  on_macos do
    on_arm do
      url "${base}/garmin-cli-${VERSION}-macos-arm64.tar.gz"
      sha256 "${SHA256_MACOS_ARM64}"
    end
    on_intel do
      url "${base}/garmin-cli-${VERSION}-macos-x86_64.tar.gz"
      sha256 "${SHA256_MACOS_X86_64}"
    end
  end

  on_linux do
    on_intel do
      url "${base}/garmin-cli-${VERSION}-linux-x86_64.tar.gz"
      sha256 "${SHA256_LINUX_X86_64}"
    end
    on_arm do
      url "${base}/garmin-cli-${VERSION}-linux-aarch64.tar.gz"
      sha256 "${SHA256_LINUX_AARCH64}"
    end
  end

  def install
    bin.install "gc"
    doc.install "THIRD_PARTY_NOTICES.md"
  end

  test do
    assert_match "Usage", shell_output("#{bin}/gc --help")
  end
end
FORMULA
