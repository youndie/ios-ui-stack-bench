#!/usr/bin/env python3
"""Generate the harness's Xcode project: one UI-testing bundle and no host app.

The scenarios drive the arms by bundle id (`XCUIApplication(bundleIdentifier:)`), so the harness
needs no app of its own. A host app would be one more install on a free account that allows three
per device (research §1.5); the runner is the only thing the harness adds.

    python3 harness/generate_project.py           write harness/Harness.xcodeproj
    python3 harness/generate_project.py --check   fail if the committed project differs
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(ROOT, "Harness.xcodeproj", "project.pbxproj")


def oid(role):
    return hashlib.sha256(f"harness/{role}".encode()).hexdigest()[:24].upper()


def settings(debug):
    return f"""				CLANG_ENABLE_MODULES = YES;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = "${{TEAM_ID}}";
				GENERATE_INFOPLIST_FILE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 18.2;
				MARKETING_VERSION = 1.0;
				PRODUCT_BUNDLE_IDENTIFIER = io.github.youndie.iosbench.harness;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				SWIFT_EMIT_LOC_STRINGS = NO;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
				SWIFT_OPTIMIZATION_LEVEL = "{'-Onone' if debug else '-O'}";
"""


def project():
    i = oid
    return f"""// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{
	}};
	objectVersion = 77;
	objects = {{

/* Begin PBXFileReference section */
		{i('product')} /* HarnessUITests.xctest */ = {{isa = PBXFileReference; explicitFileType = wrapper.cfbundle; includeInIndex = 0; path = HarnessUITests.xctest; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End PBXFileReference section */

/* Begin PBXFileSystemSynchronizedRootGroup section */
		{i('group/tests')} /* HarnessUITests */ = {{
			isa = PBXFileSystemSynchronizedRootGroup;
			path = HarnessUITests;
			sourceTree = "<group>";
		}};
		{i('group/config')} /* Configuration */ = {{
			isa = PBXFileSystemSynchronizedRootGroup;
			path = Configuration;
			sourceTree = "<group>";
		}};
/* End PBXFileSystemSynchronizedRootGroup section */

/* Begin PBXFrameworksBuildPhase section */
		{i('phase/frameworks')} /* Frameworks */ = {{
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		{i('group/main')} = {{
			isa = PBXGroup;
			children = (
				{i('group/config')} /* Configuration */,
				{i('group/tests')} /* HarnessUITests */,
				{i('group/products')} /* Products */,
			);
			sourceTree = "<group>";
		}};
		{i('group/products')} /* Products */ = {{
			isa = PBXGroup;
			children = (
				{i('product')} /* HarnessUITests.xctest */,
			);
			name = Products;
			sourceTree = "<group>";
		}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		{i('target')} /* HarnessUITests */ = {{
			isa = PBXNativeTarget;
			buildConfigurationList = {i('configs/target')} /* Build configuration list for PBXNativeTarget "HarnessUITests" */;
			buildPhases = (
				{i('phase/sources')} /* Sources */,
				{i('phase/frameworks')} /* Frameworks */,
				{i('phase/resources')} /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			fileSystemSynchronizedGroups = (
				{i('group/tests')} /* HarnessUITests */,
			);
			name = HarnessUITests;
			packageProductDependencies = (
			);
			productName = HarnessUITests;
			productReference = {i('product')} /* HarnessUITests.xctest */;
			productType = "com.apple.product-type.bundle.ui-testing";
		}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		{i('project')} /* Project object */ = {{
			isa = PBXProject;
			attributes = {{
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1620;
				LastUpgradeCheck = 1620;
			}};
			buildConfigurationList = {i('configs/project')} /* Build configuration list for PBXProject "Harness" */;
			developmentRegion = en;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
				Base,
			);
			mainGroup = {i('group/main')};
			minimizedProjectReferenceProxies = 1;
			preferredProjectObjectVersion = 77;
			productRefGroup = {i('group/products')} /* Products */;
			projectDirPath = "";
			projectRoot = "";
			targets = (
				{i('target')} /* HarnessUITests */,
			);
		}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		{i('phase/resources')} /* Resources */ = {{
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		{i('phase/sources')} /* Sources */ = {{
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		{i('config/project/Debug')} /* Debug */ = {{
			isa = XCBuildConfiguration;
			baseConfigurationReferenceAnchor = {i('group/config')} /* Configuration */;
			baseConfigurationReferenceRelativePath = Config.xcconfig;
			buildSettings = {{
				SDKROOT = iphoneos;
			}};
			name = Debug;
		}};
		{i('config/project/Release')} /* Release */ = {{
			isa = XCBuildConfiguration;
			baseConfigurationReferenceAnchor = {i('group/config')} /* Configuration */;
			baseConfigurationReferenceRelativePath = Config.xcconfig;
			buildSettings = {{
				SDKROOT = iphoneos;
			}};
			name = Release;
		}};
		{i('config/target/Debug')} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
{settings(True)}			}};
			name = Debug;
		}};
		{i('config/target/Release')} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
{settings(False)}			}};
			name = Release;
		}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		{i('configs/project')} /* Build configuration list for PBXProject "Harness" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{i('config/project/Debug')} /* Debug */,
				{i('config/project/Release')} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
		{i('configs/target')} /* Build configuration list for PBXNativeTarget "HarnessUITests" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{i('config/target/Debug')} /* Debug */,
				{i('config/target/Release')} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
/* End XCConfigurationList section */
	}};
	rootObject = {i('project')} /* Project object */;
}}
"""


def main():
    text = project()
    if "--check" in sys.argv[1:]:
        try:
            current = open(PATH, encoding="utf-8").read()
        except FileNotFoundError:
            current = None
        if current != text:
            print("stale harness project - run python3 harness/generate_project.py")
            return 1
        print("harness project matches the generator")
        return 0
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print("harness project written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
