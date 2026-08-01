const fs = require('fs');
const path = require('path');

const rootDir = '/workspace/starlight-carnival';

// 需要添加手势指引开关的页面列表
const pages = [
  'home-v2.html',
  'player-select.html',
  'world-map-v2.html', // 已修复，跳过
  'bubble-bay-v2.html',
  'bubble-bay-v3.html',
  'bubble-bay-turtle.html',
  'bubble-bay-clownfish.html',
  'bubble-bay-octopus.html',
  'echo-valley-v2.html',
  'echo-valley-v3.html',
  'echo-valley-parrot.html',
  'echo-valley-owl.html',
  'shadow-jungle-v2.html',
  'shadow-jungle-v3.html',
  'shadow-jungle-sloth.html',
  'shadow-jungle-monkey.html',
  'shadow-jungle-chameleon.html',
  'starlight-midchapter.html',
  'starlight-finale-v2.html',
  'index.html'
];

let updatedCount = 0;

pages.forEach(file => {
  const filePath = path.join(rootDir, file);
  if (!fs.existsSync(filePath)) {
    console.log(`Skipped (not found): ${file}`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // 跳过已经有 gesture-guide-toggle 的文件
  if (content.includes('gesture-guide-toggle')) {
    console.log(`Skipped (already has toggle): ${file}`);
    return;
  }
  
  let changed = false;
  
  // 1. 在语音引导开关后面添加手势指引开关
  const oldToggle = /(<div class="voice-setting-row">\s*<span class="voice-setting-label">语音引导<\/span>\s*<button id="voice-guide-toggle" class="voice-toggle on" aria-label="语音引导开关"><\/button>\s*<\/div>)/;
  
  if (oldToggle.test(content)) {
    const newToggle = `$1
    <div class="voice-setting-row">
      <span class="voice-setting-label">手势指引</span>
      <button id="gesture-guide-toggle" class="voice-toggle on" aria-label="手势指引开关"></button>
    </div>`;
    content = content.replace(oldToggle, newToggle);
    changed = true;
  } else {
    // 尝试另一种格式
    const oldToggle2 = /(<div class="voice-setting-row">\s*<span class="voice-setting-label">语音引导<\/span>\s*<button class="voice-toggle on" id="voice-guide-toggle"[^>]*><\/button>\s*<\/div>)/;
    if (oldToggle2.test(content)) {
      const newToggle = `$1
    <div class="voice-setting-row">
      <span class="voice-setting-label">手势指引</span>
      <button id="gesture-guide-toggle" class="voice-toggle on" aria-label="手势指引开关"></button>
    </div>`;
      content = content.replace(oldToggle2, newToggle);
      changed = true;
    }
  }
  
  // 2. 在 DOMContentLoaded 中添加手势指引开关的初始化代码
  if (changed) {
    // 在 toggle 变量声明后面添加 gestureToggle
    const oldDecl = /(const toggle = document.getElementById\('voice-guide-toggle'\);)/;
    if (oldDecl.test(content)) {
      content = content.replace(oldDecl, `$1
      const gestureToggle = document.getElementById('gesture-guide-toggle');`);
    }
    
    // 在语音引导开关状态初始化后面添加手势指引初始化
    const oldInit = /(if \(isVoiceGuideEnabled\(\)\) \{\s*if \(toggle\) toggle\.classList\.add\('on'\);\s*\} else \{\s*if \(toggle\) toggle\.classList\.remove\('on'\);\s*\})/;
    if (oldInit.test(content)) {
      const newInit = `$1
      
      if (localStorage.getItem('starlight_gesture_enabled') !== 'false') {
        if (gestureToggle) gestureToggle.classList.add('on');
      } else {
        if (gestureToggle) gestureToggle.classList.remove('on');
      }`;
      content = content.replace(oldInit, newInit);
    }
    
    // 在语音开关事件监听器后面添加手势指引开关监听器
    const oldListener = /(if \(toggle\) \{\s*toggle\.addEventListener\('click', function\(\) \{\s*const enabled = !isVoiceGuideEnabled\(\);\s*setVoiceGuideEnabled\(enabled\);\s*if \(enabled\) \{\s*toggle\.classList\.add\('on'\);\s*\} else \{\s*toggle\.classList\.remove\('on'\);\s*\}\s*\}\);\s*\})/;
    if (oldListener.test(content)) {
      const newListener = `$1
      
      if (gestureToggle) {
        gestureToggle.addEventListener('click', function() {
          const enabled = localStorage.getItem('starlight_gesture_enabled') !== 'false';
          localStorage.setItem('starlight_gesture_enabled', enabled ? 'false' : 'true');
          if (!enabled) {
            gestureToggle.classList.add('on');
          } else {
            gestureToggle.classList.remove('on');
          }
          if (window.GestureGuide && window.GestureGuide.setEnabled) {
            window.GestureGuide.setEnabled(!enabled);
          }
        });
      }`;
      content = content.replace(oldListener, newListener);
    }
    
    fs.writeFileSync(filePath, content, 'utf8');
    updatedCount++;
    console.log(`Updated: ${file}`);
  } else {
    console.log(`Pattern not found: ${file}`);
  }
});

console.log(`\nTotal updated: ${updatedCount} files`);
