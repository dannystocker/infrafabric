/**
 * IF.deliberate - Natural Typing Stream with Deliberate Word Replacement
 *
 * Features:
 * - QWERTY keyboard distance-based typing speed
 * - Frequent letter corrections (typos with backspace)
 * - Occasional word replacements (deliberate emphasis)
 * - Blinking console-like cursor
 * - Natural pauses for thinking
 * - Thoughts come in chunks (not continuous stream)
 */

class NaturalTypingStream {
  constructor(containerElement, options = {}) {
    this.container = containerElement;
    this.options = {
      baseTypingSpeed: 80, // milliseconds per character
      typoFrequency: 0.05, // 5% chance of typo per character
      replacementFrequency: 0.03, // 3% chance of word replacement
      thinkingPauseMin: 300, // minimum pause between thought chunks
      thinkingPauseMax: 1200, // maximum pause between thought chunks
      cursorBlinkRate: 530, // milliseconds
      ...options
    };

    this.textElement = null;
    this.cursorElement = null;
    this.currentText = '';
    this.isTyping = false;
    this.cursorInterval = null;

    this._initializeCursor();
    this._initializeQwertyLayout();
  }

  /**
   * QWERTY keyboard layout for distance calculation
   */
  _initializeQwertyLayout() {
    this.qwertyLayout = {
      'q': {x: 0, y: 0}, 'w': {x: 1, y: 0}, 'e': {x: 2, y: 0}, 'r': {x: 3, y: 0}, 't': {x: 4, y: 0},
      'y': {x: 5, y: 0}, 'u': {x: 6, y: 0}, 'i': {x: 7, y: 0}, 'o': {x: 8, y: 0}, 'p': {x: 9, y: 0},
      'a': {x: 0, y: 1}, 's': {x: 1, y: 1}, 'd': {x: 2, y: 1}, 'f': {x: 3, y: 1}, 'g': {x: 4, y: 1},
      'h': {x: 5, y: 1}, 'j': {x: 6, y: 1}, 'k': {x: 7, y: 1}, 'l': {x: 8, y: 1},
      'z': {x: 0, y: 2}, 'x': {x: 1, y: 2}, 'c': {x: 2, y: 2}, 'v': {x: 3, y: 2}, 'b': {x: 4, y: 2},
      'n': {x: 5, y: 2}, 'm': {x: 6, y: 2},
      ' ': {x: 4, y: 3} // spacebar in middle
    };

    // Adjacent keys for realistic typos
    this.adjacentKeys = {
      'a': ['q', 's', 'w', 'z'],
      'b': ['v', 'g', 'h', 'n'],
      'c': ['x', 'd', 'f', 'v'],
      'd': ['s', 'e', 'r', 'f', 'c', 'x'],
      'e': ['w', 's', 'd', 'r'],
      'f': ['d', 'r', 't', 'g', 'v', 'c'],
      'g': ['f', 't', 'y', 'h', 'b', 'v'],
      'h': ['g', 'y', 'u', 'j', 'n', 'b'],
      'i': ['u', 'j', 'k', 'o'],
      'j': ['h', 'u', 'i', 'k', 'n', 'm'],
      'k': ['j', 'i', 'o', 'l', 'm'],
      'l': ['k', 'o', 'p'],
      'm': ['n', 'j', 'k'],
      'n': ['b', 'h', 'j', 'm'],
      'o': ['i', 'k', 'l', 'p'],
      'p': ['o', 'l'],
      'q': ['w', 'a'],
      'r': ['e', 'd', 'f', 't'],
      's': ['a', 'w', 'e', 'd', 'x', 'z'],
      't': ['r', 'f', 'g', 'y'],
      'u': ['y', 'h', 'j', 'i'],
      'v': ['c', 'f', 'g', 'b'],
      'w': ['q', 'e', 's', 'a'],
      'x': ['z', 's', 'd', 'c'],
      'y': ['t', 'g', 'h', 'u'],
      'z': ['a', 's', 'x']
    };
  }

  /**
   * Initialize blinking cursor
   */
  _initializeCursor() {
    this.textElement = document.createElement('span');
    this.textElement.className = 'typing-text';

    this.cursorElement = document.createElement('span');
    this.cursorElement.className = 'typing-cursor';
    this.cursorElement.textContent = '▊';
    this.cursorElement.style.opacity = '1';

    this.container.innerHTML = '';
    this.container.appendChild(this.textElement);
    this.container.appendChild(this.cursorElement);

    // Start cursor blinking
    this.cursorInterval = setInterval(() => {
      this.cursorElement.style.opacity =
        this.cursorElement.style.opacity === '1' ? '0' : '1';
    }, this.options.cursorBlinkRate);
  }

  /**
   * Calculate typing delay based on QWERTY keyboard distance
   */
  _calculateTypingDelay(prevChar, nextChar) {
    const prev = prevChar?.toLowerCase() || ' ';
    const next = nextChar?.toLowerCase() || ' ';

    const prevPos = this.qwertyLayout[prev];
    const nextPos = this.qwertyLayout[next];

    if (!prevPos || !nextPos) {
      return this.options.baseTypingSpeed + this._jitter();
    }

    // Euclidean distance
    const distance = Math.sqrt(
      Math.pow(nextPos.x - prevPos.x, 2) +
      Math.pow(nextPos.y - prevPos.y, 2)
    );

    // Farther keys take longer
    const distanceMultiplier = 30;
    return this.options.baseTypingSpeed + (distance * distanceMultiplier) + this._jitter();
  }

  /**
   * Random timing jitter for natural variation
   */
  _jitter() {
    return Math.random() * 100 - 50; // ±50ms
  }

  /**
   * Get random typo for a character
   */
  _getTypo(char) {
    const lower = char.toLowerCase();
    const adjacent = this.adjacentKeys[lower];
    if (!adjacent || adjacent.length === 0) return char;

    const typo = adjacent[Math.floor(Math.random() * adjacent.length)];
    return char === char.toUpperCase() ? typo.toUpperCase() : typo;
  }

  /**
   * Type a single character with optional typo
   */
  async _typeCharacter(char, prevChar) {
    const delay = this._calculateTypingDelay(prevChar, char);

    // Random typo?
    if (Math.random() < this.options.typoFrequency && char.match(/[a-z]/i)) {
      const typo = this._getTypo(char);

      // Type typo
      await this._sleep(delay);
      this.currentText += typo;
      this.textElement.textContent = this.currentText;

      // Pause (realize mistake)
      await this._sleep(150);

      // Backspace
      await this._sleep(50);
      this.currentText = this.currentText.slice(0, -1);
      this.textElement.textContent = this.currentText;

      // Type correct character
      await this._sleep(delay * 0.8);
      this.currentText += char;
      this.textElement.textContent = this.currentText;
    } else {
      // Type normally
      await this._sleep(delay);
      this.currentText += char;
      this.textElement.textContent = this.currentText;
    }
  }

  /**
   * Type a word with potential replacement
   */
  async _typeWord(word, shouldReplace = false, replacement = null) {
    // Type the word character by character
    for (let i = 0; i < word.length; i++) {
      const prevChar = i > 0 ? word[i - 1] : (this.currentText.slice(-1) || ' ');
      await this._typeCharacter(word[i], prevChar);
    }

    // Deliberate word replacement?
    if (shouldReplace && replacement) {
      // Pause (reconsider)
      await this._sleep(150);

      // Backspace entire word
      for (let i = 0; i < word.length; i++) {
        await this._sleep(50);
        this.currentText = this.currentText.slice(0, -1);
        this.textElement.textContent = this.currentText;
      }

      // Pause before typing replacement
      await this._sleep(200);

      // Type replacement
      for (let i = 0; i < replacement.length; i++) {
        const prevChar = i > 0 ? replacement[i - 1] : (this.currentText.slice(-1) || ' ');
        await this._typeCharacter(replacement[i], prevChar);
      }
    }
  }

  /**
   * Natural pause for thinking between thought chunks
   */
  async _thinkingPause() {
    const pause = this.options.thinkingPauseMin +
      Math.random() * (this.options.thinkingPauseMax - this.options.thinkingPauseMin);
    await this._sleep(pause);
  }

  /**
   * Process streaming chunk with word replacements
   */
  async streamChunk(chunk, replacements = []) {
    if (!this.isTyping) {
      this.isTyping = true;
      this.cursorElement.style.opacity = '1'; // Show cursor during typing
    }

    // Split chunk into words
    const words = chunk.split(/(\s+)/); // Preserve whitespace

    for (let i = 0; i < words.length; i++) {
      const word = words[i];

      // Check if this word should be replaced
      const replacement = replacements.find(r => r.index === i);

      await this._typeWord(
        word,
        !!replacement,
        replacement?.replacement
      );
    }
  }

  /**
   * Stream complete message with natural thinking pauses
   */
  async streamMessage(messageChunks, replacementMap = {}) {
    this.reset();

    for (let i = 0; i < messageChunks.length; i++) {
      const chunk = messageChunks[i];
      const replacements = replacementMap[i] || [];

      await this.streamChunk(chunk, replacements);

      // Natural pause between thought chunks (except after last chunk)
      if (i < messageChunks.length - 1) {
        await this._thinkingPause();
      }
    }

    this.isTyping = false;
  }

  /**
   * Reset typing state
   */
  reset() {
    this.currentText = '';
    this.textElement.textContent = '';
    this.isTyping = false;
  }

  /**
   * Clean up
   */
  destroy() {
    if (this.cursorInterval) {
      clearInterval(this.cursorInterval);
    }
  }

  /**
   * Sleep helper
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Example usage
if (typeof window !== 'undefined') {
  window.NaturalTypingStream = NaturalTypingStream;
}

// Example with IF.deliberate word replacements
/*
const container = document.getElementById('chat-message');
const stream = new NaturalTypingStream(container);

// Message split into thought chunks
const messageChunks = [
  "Your approach is",
  "practical and well thought out.",
  "I especially appreciate how you've considered the edge cases."
];

// Word replacements for IF.deliberate feature
const replacementMap = {
  0: [
    { index: 2, replacement: "brilliant" } // Replace "practical" with "brilliant"
  ],
  2: [
    { index: 1, replacement: "deeply" }, // Replace "especially" with "deeply"
    { index: 6, replacement: "anticipated" } // Replace "considered" with "anticipated"
  ]
};

stream.streamMessage(messageChunks, replacementMap);
*/
