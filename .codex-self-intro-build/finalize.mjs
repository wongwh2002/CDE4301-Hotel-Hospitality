import path from 'node:path';
import { pathToFileURL } from 'node:url';

const workspaceDir = process.cwd();
const buildDir = path.join(workspaceDir, '.codex-self-intro-build');
const skillDir = '/Users/wongwh/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations';
const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, 'container_tools/artifact_tool_utils.mjs')).href);

const result = await finalizePresentation({
  workspaceDir,
  candidatePath: path.join(buildDir, 'candidate.pptx'),
  finalPath: path.join(workspaceDir, 'deliverables', 'self_intro_day_in_life.pptx'),
  pythonExecutable: '/Users/wongwh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
  integrityValidatorPath: path.join(skillDir, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skillDir, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: [
    '--expected-slide-size-emu', '12192000,6858000',
    '--validate-bullet-geometry',
    '--validate-heading-fit',
  ],
  explicitTotalSlideCount: 2,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: 'design', families: ['Helvetica Neue'] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(buildDir, 'validation.json'),
});

console.log(JSON.stringify({ finalPath: result.finalPath, finalSha256: result.finalSha256, receiptPath: result.receiptPath }));
