import fs from 'node:fs/promises';
import path from 'node:path';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const workspaceDir = process.cwd();
const buildDir = path.join(workspaceDir, '.codex-self-intro-build');
const previewDir = path.join(buildDir, 'preview');
const candidatePath = path.join(buildDir, 'candidate.pptx');

const introImages = [
  { filename: '01-coffee-espresso-machine-modded.jpg', alt: 'Modified home espresso machine and grinder.', pair: 'coffee' },
  { filename: '02-coffee-filter-brew.jpg', alt: 'A filter coffee tasting beside a cup of coffee.', pair: 'coffee' },
  { filename: '03-food-trip.jpg', alt: 'A meal during a food outing.', pair: 'food' },
  { filename: '04-steak-cooking.jpg', alt: 'A home-cooked meal with steak.', pair: 'food' },
  { filename: '05-tiramisu-expectation.jpg', alt: 'A slice of tiramisu.', pair: 'tiramisu' },
  { filename: '06-tiramisu-reality.jpg', alt: 'The remains of a homemade tiramisu attempt.', pair: 'tiramisu' },
  { filename: '07-drinks-basket.jpg', alt: 'A basket of assorted drinks.', pair: 'drinks' },
  { filename: '08-bar-scene.jpg', alt: 'A bar counter and beer tap.', pair: 'drinks' },
].map((item) => ({ ...item, directory: 'self-intro' }));

const dayImages = [
  { filename: '01-laptop-video-call.jpg', alt: 'Laptop open during a video call.', directory: 'day-in-life' },
  { filename: '02-project-meeting.jpg', alt: 'Students working together in a project meeting.', directory: 'day-in-life' },
  { filename: '03-cafe-collaboration.jpg', alt: 'A group meeting around a table in a bright cafe.', directory: 'day-in-life' },
  { filename: '04-classroom-work.jpg', alt: 'A laptop ready for class or study.', directory: 'day-in-life' },
  { filename: '05-lunch-crowd.jpg', alt: 'A crowded lunch gathering.', directory: 'day-in-life' },
  { filename: '06-food-street.jpg', alt: 'A busy food and shopping street.', directory: 'day-in-life' },
];

async function readImage(item) {
  const filePath = path.join(workspaceDir, 'deliverables', item.directory, item.filename);
  const bytes = await fs.readFile(filePath);
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function addImage(slide, item, blob, position, name) {
  slide.images.add({
    name,
    blob,
    contentType: 'image/jpeg',
    alt: item.alt,
    fit: 'cover',
    position,
  });
}

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

// Slide 1: Four grouped photo pairs, with no visible text.
const introSlide = presentation.slides.add();
introSlide.background.fill = '#000000';
const introBlobs = await Promise.all(introImages.map(readImage));
const groupPositions = [
  { left: 32, top: 40 },
  { left: 646, top: 40 },
  { left: 32, top: 378 },
  { left: 646, top: 378 },
];
const imageWidth = 295;
const imageHeight = 302;
const pairGap = 12;
for (let pairIndex = 0; pairIndex < 4; pairIndex += 1) {
  const position = groupPositions[pairIndex];
  const first = pairIndex * 2;
  await addImage(introSlide, introImages[first], introBlobs[first], {
    left: position.left,
    top: position.top,
    width: imageWidth,
    height: imageHeight,
  }, `${introImages[first].pair}-1`);
  await addImage(introSlide, introImages[first + 1], introBlobs[first + 1], {
    left: position.left + imageWidth + pairGap,
    top: position.top,
    width: imageWidth,
    height: imageHeight,
  }, `${introImages[first].pair}-2`);
}

// Slide 2: A day-in-life montage. Work and class lead into the crowd and food-street punchline.
const daySlide = presentation.slides.add();
daySlide.background.fill = '#000000';
const dayBlobs = await Promise.all(dayImages.map(readImage));
const topRow = { top: 36, width: 282, height: 216, gap: 22, startLeft: 28 };
for (let index = 0; index < 4; index += 1) {
  await addImage(daySlide, dayImages[index], dayBlobs[index], {
    left: topRow.startLeft + index * (topRow.width + topRow.gap),
    top: topRow.top,
    width: topRow.width,
    height: topRow.height,
  }, `day-work-${index + 1}`);
}
const bottomRow = { top: 274, width: 596, height: 410, gap: 32, startLeft: 28 };
for (let index = 4; index < 6; index += 1) {
  const column = index - 4;
  await addImage(daySlide, dayImages[index], dayBlobs[index], {
    left: bottomRow.startLeft + column * (bottomRow.width + bottomRow.gap),
    top: bottomRow.top,
    width: bottomRow.width,
    height: bottomRow.height,
  }, `day-punchline-${column + 1}`);
}

await fs.mkdir(previewDir, { recursive: true });
for (const [index, slide] of presentation.slides.items.entries()) {
  const preview = await presentation.export({ slide, format: 'png', scale: 1 });
  await fs.writeFile(path.join(previewDir, `slide-${index + 1}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(candidatePath);
console.log(JSON.stringify({ candidatePath, slideCount: presentation.slides.items.length, imageCount: introImages.length + dayImages.length, previewDir }));
