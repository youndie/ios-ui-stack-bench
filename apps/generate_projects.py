#!/usr/bin/env python3
"""Generate the Xcode project of every arm from one template — the KMP wizard's.

Five apps that are meant to differ only in their UI stack and their bridge must not differ in a
build setting nobody chose. So there is one project template, and this script is the only place
the arms differ: the product name, the Gradle task that builds the Kotlin side (none for A), and
which shared Swift sources (`apps/common/...`) each target compiles.

The template is `iosApp/iosApp.xcodeproj/project.pbxproj` of the KMP wizard's native-UI branch,
Kotlin/kmp-wizard@8fa355754f55454e0e2e72a6c0b4e29052ed5b7d, with its build settings unchanged.
Object ids are derived from the arm and the object's role, so a re-run is byte-identical.

    python3 apps/generate_projects.py           write apps/<arm>/iosApp.xcodeproj/project.pbxproj
    python3 apps/generate_projects.py --check   fail if a committed project differs from the output
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# arm directory -> (product name, Gradle task or None, shared source folders under apps/common)
ARMS = {
    "a-native": ("BenchA", None, ["Instrumentation", "ListUI", "Fixture", "Thumbnails"]),
    "b1-objc": ("BenchB1", ":bridge-objc:embedAndSignAppleFrameworkForXcode", ["Instrumentation", "ListUI", "Fixture", "Thumbnails"]),
    "b2-skie": ("BenchB2", ":bridge-skie:embedAndSignAppleFrameworkForXcode", ["Instrumentation", "ListUI", "Fixture", "Thumbnails"]),
    "b3-swift-export": ("BenchB3", ":bridge-swift-export:embedSwiftExportForXcode", ["Instrumentation", "ListUI", "Fixture", "Thumbnails"]),
    # C draws the thumbnails as Compose resources, which its framework build bundles itself.
    "c-kmp-cmp": ("BenchC", ":compose-ui:embedAndSignAppleFrameworkForXcode", ["Instrumentation", "Fixture"]),
}


def oid(arm, role):
    return hashlib.sha256(f"{arm}/{role}".encode()).hexdigest()[:24].upper()


COMMON_SETTINGS = """				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
				CLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_ENABLE_OBJC_WEAK = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				COPY_PHASE_STRIP = NO;
"""

TARGET_SETTINGS = """				ARCHS = arm64;
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
				CODE_SIGN_IDENTITY = "Apple Development";
				CODE_SIGN_STYLE = Automatic;
				DEVELOPMENT_ASSET_PATHS = "\\"iosApp/Preview Content\\"";
				DEVELOPMENT_TEAM = "${TEAM_ID}";
				ENABLE_PREVIEWS = YES;
				GENERATE_INFOPLIST_FILE = YES;
				INFOPLIST_FILE = iosApp/Info.plist;
				INFOPLIST_KEY_UIApplicationSceneManifest_Generation = YES;
				INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents = YES;
				INFOPLIST_KEY_UILaunchScreen_Generation = YES;
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
"""


def project(arm, product, task, shared):
    i = lambda role: oid(arm, role)
    shared_groups = "".join(
        f"""		{i('group/' + s)} /* {s} */ = {{
			isa = PBXFileSystemSynchronizedRootGroup;
			path = ../common/{s};
			sourceTree = "<group>";
		}};
""" for s in shared)
    shared_children = "".join(f"				{i('group/' + s)} /* {s} */,\n" for s in shared)
    if task:
        script = ("if [ \\\"YES\\\" = \\\"$OVERRIDE_KOTLIN_BUILD_IDE_SUPPORTED\\\" ]; then\\n"
                  "  echo \\\"Skipping Gradle build task invocation due to OVERRIDE_KOTLIN_BUILD_IDE_SUPPORTED environment variable set to \\\\\\\"YES\\\\\\\"\\\"\\n"
                  "  exit 0\\n"
                  "fi\\n"
                  "cd \\\"$SRCROOT/../..\\\"\\n"
                  f"./gradlew {task}\\n")
        kotlin_phase_ref = f"				{i('phase/kotlin')} /* Compile Kotlin Framework */,\n"
        kotlin_phase = f"""/* Begin PBXShellScriptBuildPhase section */
		{i('phase/kotlin')} /* Compile Kotlin Framework */ = {{
			isa = PBXShellScriptBuildPhase;
			alwaysOutOfDate = 1;
			buildActionMask = 2147483647;
			files = (
			);
			inputFileListPaths = (
			);
			inputPaths = (
			);
			name = "Compile Kotlin Framework";
			outputFileListPaths = (
			);
			outputPaths = (
			);
			runOnlyForDeploymentPostprocessing = 0;
			shellPath = /bin/sh;
			shellScript = "{script}";
		}};
/* End PBXShellScriptBuildPhase section */

"""
    else:
        kotlin_phase_ref = ""
        kotlin_phase = ""
    return f"""// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{
	}};
	objectVersion = 77;
	objects = {{

/* Begin PBXFileReference section */
		{i('product')} /* {product}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {product}.app; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End PBXFileReference section */

/* Begin PBXFileSystemSynchronizedBuildFileExceptionSet section */
		{i('exceptions')} /* Exceptions for "iosApp" folder in "iosApp" target */ = {{
			isa = PBXFileSystemSynchronizedBuildFileExceptionSet;
			membershipExceptions = (
				Info.plist,
			);
			target = {i('target')} /* iosApp */;
		}};
/* End PBXFileSystemSynchronizedBuildFileExceptionSet section */

/* Begin PBXFileSystemSynchronizedRootGroup section */
		{i('group/iosApp')} /* iosApp */ = {{
			isa = PBXFileSystemSynchronizedRootGroup;
			exceptions = (
				{i('exceptions')} /* Exceptions for "iosApp" folder in "iosApp" target */,
			);
			path = iosApp;
			sourceTree = "<group>";
		}};
		{i('group/Configuration')} /* Configuration */ = {{
			isa = PBXFileSystemSynchronizedRootGroup;
			path = Configuration;
			sourceTree = "<group>";
		}};
{shared_groups}/* End PBXFileSystemSynchronizedRootGroup section */

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
				{i('group/Configuration')} /* Configuration */,
				{i('group/iosApp')} /* iosApp */,
{shared_children}				{i('group/products')} /* Products */,
			);
			sourceTree = "<group>";
		}};
		{i('group/products')} /* Products */ = {{
			isa = PBXGroup;
			children = (
				{i('product')} /* {product}.app */,
			);
			name = Products;
			sourceTree = "<group>";
		}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		{i('target')} /* iosApp */ = {{
			isa = PBXNativeTarget;
			buildConfigurationList = {i('configs/target')} /* Build configuration list for PBXNativeTarget "iosApp" */;
			buildPhases = (
{kotlin_phase_ref}				{i('phase/sources')} /* Sources */,
				{i('phase/frameworks')} /* Frameworks */,
				{i('phase/resources')} /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			fileSystemSynchronizedGroups = (
				{i('group/iosApp')} /* iosApp */,
{shared_children.replace(i('group/products'), '')}			);
			name = iosApp;
			packageProductDependencies = (
			);
			productName = iosApp;
			productReference = {i('product')} /* {product}.app */;
			productType = "com.apple.product-type.application";
		}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		{i('project')} /* Project object */ = {{
			isa = PBXProject;
			attributes = {{
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1620;
				LastUpgradeCheck = 1620;
				TargetAttributes = {{
					{i('target')} = {{
						CreatedOnToolsVersion = 16.2;
					}};
				}};
			}};
			buildConfigurationList = {i('configs/project')} /* Build configuration list for PBXProject "iosApp" */;
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
				{i('target')} /* iosApp */,
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

{kotlin_phase}/* Begin PBXSourcesBuildPhase section */
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
			baseConfigurationReferenceAnchor = {i('group/Configuration')} /* Configuration */;
			baseConfigurationReferenceRelativePath = Config.xcconfig;
			buildSettings = {{
{COMMON_SETTINGS}				DEBUG_INFORMATION_FORMAT = dwarf;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = NO;
				GCC_C_LANGUAGE_STANDARD = gnu17;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 18.2;
				LOCALIZATION_PREFERS_STRING_CATALOGS = YES;
				MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
				MTL_FAST_MATH = YES;
				ONLY_ACTIVE_ARCH = YES;
				SDKROOT = iphoneos;
				SWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)";
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
			}};
			name = Debug;
		}};
		{i('config/project/Release')} /* Release */ = {{
			isa = XCBuildConfiguration;
			baseConfigurationReferenceAnchor = {i('group/Configuration')} /* Configuration */;
			baseConfigurationReferenceRelativePath = Config.xcconfig;
			buildSettings = {{
{COMMON_SETTINGS}				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = NO;
				GCC_C_LANGUAGE_STANDARD = gnu17;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 18.2;
				LOCALIZATION_PREFERS_STRING_CATALOGS = YES;
				MTL_ENABLE_DEBUG_INFO = NO;
				MTL_FAST_MATH = YES;
				SDKROOT = iphoneos;
				SWIFT_COMPILATION_MODE = wholemodule;
				VALIDATE_PRODUCT = YES;
			}};
			name = Release;
		}};
		{i('config/target/Debug')} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
{TARGET_SETTINGS}			}};
			name = Debug;
		}};
		{i('config/target/Release')} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
{TARGET_SETTINGS}			}};
			name = Release;
		}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		{i('configs/project')} /* Build configuration list for PBXProject "iosApp" */ = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{i('config/project/Debug')} /* Debug */,
				{i('config/project/Release')} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
		{i('configs/target')} /* Build configuration list for PBXNativeTarget "iosApp" */ = {{
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
    check = "--check" in sys.argv[1:]
    stale = []
    for arm, (product, task, shared) in ARMS.items():
        path = os.path.join(ROOT, arm, "iosApp.xcodeproj", "project.pbxproj")
        text = project(arm, product, task, shared)
        if check:
            try:
                current = open(path, encoding="utf-8").read()
            except FileNotFoundError:
                current = None
            if current != text:
                stale.append(path)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
    if stale:
        print("stale Xcode projects - run python3 apps/generate_projects.py:\n  " + "\n  ".join(stale))
        return 1
    print("Xcode projects " + ("match the generator" if check else "written") + f": {len(ARMS)} arms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
