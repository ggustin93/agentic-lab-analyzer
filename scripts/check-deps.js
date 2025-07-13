#!/usr/bin/env node

const packageJson = require('./package.json');

console.log('🔍 Checking npm dependencies...');

const dependencies = packageJson.dependencies;
const problematicPackages = [];

// Check for known problematic packages
const knownIssues = {
  'ngx-extended-pdf-viewer': 'Use ng2-pdf-viewer instead for Angular 19 compatibility',
  '@angular/core': 'Should be ^19.0.0 for Angular 19 project'
};

Object.keys(dependencies).forEach(pkg => {
  if (knownIssues[pkg]) {
    problematicPackages.push({
      package: pkg,
      version: dependencies[pkg],
      issue: knownIssues[pkg]
    });
  }
});

// Check Angular version consistency
const angularPackages = Object.keys(dependencies).filter(pkg => pkg.startsWith('@angular/'));
const angularVersions = new Set(angularPackages.map(pkg => dependencies[pkg]));

if (angularVersions.size > 1) {
  console.log('⚠️  Warning: Multiple Angular versions detected:');
  angularPackages.forEach(pkg => {
    console.log(`  ${pkg}: ${dependencies[pkg]}`);
  });
}

// Check current package
if (dependencies['ng2-pdf-viewer']) {
  console.log('✅ PDF viewer: ng2-pdf-viewer found');
} else if (dependencies['ngx-extended-pdf-viewer']) {
  console.log('❌ PDF viewer: ngx-extended-pdf-viewer found (should use ng2-pdf-viewer)');
} else {
  console.log('ℹ️  No PDF viewer package found');
}

// Summary
if (problematicPackages.length === 0) {
  console.log('✅ All dependencies look good!');
} else {
  console.log('❌ Found potential issues:');
  problematicPackages.forEach(({ package, version, issue }) => {
    console.log(`  ${package}@${version}: ${issue}`);
  });
}

console.log(`\n📦 Total dependencies: ${Object.keys(dependencies).length}`);
console.log(`🔧 Angular version: ${dependencies['@angular/core'] || 'not found'}`);
console.log(`📄 PDF viewer: ${dependencies['ng2-pdf-viewer'] ? 'ng2-pdf-viewer' : dependencies['ngx-extended-pdf-viewer'] ? 'ngx-extended-pdf-viewer' : 'none'}`);