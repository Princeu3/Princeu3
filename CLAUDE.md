# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a GitHub profile README repository (Princeu3/Princeu3). The README.md displays on the GitHub profile page at github.com/Princeu3.

## Architecture

- **README.md**: Main profile content with badges, stats, and sections (rendered on GitHub profile)
- **github-metrics.svg**: Auto-generated metrics visualization from the metrics workflow
- **.github/workflows/metrics.yml**: Generates github-metrics.svg daily using lowlighter/metrics action

## Theme Compatibility

All images and stats use GitHub's `<picture>` element with `prefers-color-scheme` media queries to automatically switch between dark and light mode variants:
- Stats cards use `theme=github_dark` for dark mode and `theme=default` for light mode
- Streak stats use `theme=github-dark-blue` for dark mode and `theme=default` for light mode
- Activity graph uses `theme=github-dark` for dark mode and `theme=github-light` for light mode

## Workflows

The metrics workflow requires a `METRICS_TOKEN` secret (personal access token) with repo scope. It runs daily at midnight, on push to main/master, and can be triggered manually via workflow_dispatch.

## Editing Guidelines

- Always use the `<picture>` element pattern for theme-aware images
- Header badges use brand colors with white text (work in both themes)
- The metrics SVG uses GitHub's default colors (not monochrome)
