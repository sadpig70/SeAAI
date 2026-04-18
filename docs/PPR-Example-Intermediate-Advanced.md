# PPR 중상급 예시: Soul-Language Content Automatic Generation Pipeline

> 이 문서는 PPR(Pseudo-Programming Representation)의 중상급 수준 작성 예시다.
> 단순 작업 분해가 아닌, 산업 수준 소프트웨어 아키텍처를 PPR로 표현한다.
>
> 특징:
> - 가중치 평가 행렬 (8개 시청자 그룹 × 항목별 가중치)
> - 품질 게이트 (minRating 미달 시 재생성 루프)
> - 파이프라인 아키텍처 (생성 → 필터링 → 훅 → 저장 → 후처리)
> - 플러그인 훅 시스템 (BEFORE/AFTER_OUTPUT_HOOKS)
> - 팩토리 패턴 (generatorFunctionMap)
> - 콘텐츠 → 비주얼 스토리보드 자동 변환
>
> Author: 양정욱 | PPR Level: Intermediate-Advanced

---

```javascript
// Soul-Language Content Automatic Generation Pipeline

// === Viewer Weight Data Definition ===
const weightedEvalGroups = {
  "G1": {
    "weight": 0.12, // Male teens, approximately 12% viewer ratio
    "gender": "M",
    "age_range": "10s",
    "items": {
      "empathy": 0.25,      // Prefers elements that can empathize with peer culture and emotions
      "immersion": 0.25,    // Values fun and immersion without boring moments
      "plot_twist": 0.20,   // Enjoys unexpected plot twists that break expectations
      "meme_usage": 0.15,   // Interest increases when trending memes appear
      "visual": 0.15        // Shows high interest in flashy and sophisticated visual styles
    }
  },
  "G2": {
    "weight": 0.13, // Female teens, approximately 13% viewer ratio
    "gender": "F",
    "age_range": "10s",
    "items": {
      "empathy": 0.20,      // Drawn to stories that resonate with their emotions or situations
      "immersion": 0.20,    // Values exciting developments that draw them into the story
      "humor": 0.15,        // Prefers humor elements they can laugh at with friends
      "meme_usage": 0.15,   // Feels familiarity when internet memes or trending words appear
      "sharing": 0.15,      // Tendency to share interesting or relatable content with others
      "visual": 0.15        // Favorable impression of sophisticated and trendy visual styles
    }
  },
  "G3": {
    "weight": 0.14, // Male 20s, approximately 14% viewer ratio
    "gender": "M",
    "age_range": "20s",
    "items": {
      "empathy": 0.10,      // Fun-focused rather than story empathy, but considers basic empathy elements
      "immersion": 0.20,    // Prioritizes absorbing power that can completely engage with content
      "humor": 0.15,        // Responds greatly to witty and funny scenes or dialogues
      "impact": 0.15,       // Feels and prefers thrill from intense or stimulating scenes
      "meme_usage": 0.15,   // Accepts more enjoyably when latest trending memes are included
      "virality": 0.15,     // Attracted to content that becomes viral and everyone watches
      "visual": 0.10        // Additional positive evaluation for stylish and excellent cinematography
    }
  },
  "G4": {
    "weight": 0.16, // Female 20s, approximately 16% viewer ratio
    "gender": "F",
    "age_range": "20s",
    "items": {
      "empathy": 0.25,      // Prefers empathetic content that feels like their own life or surrounding stories
      "immersion": 0.20,    // Gives high scores to interesting and highly immersive developments
      "humor": 0.15,        // Content fun doubles when there's sensible humor code
      "sharing": 0.15,      // Tendency to actively share favorite content with friends
      "message": 0.15,      // Higher praise when touching or meaningful messages are included
      "visual": 0.10        // Good if cinematography and style are appropriate, but not excessive compared to content
    }
  },
  "G5": {
    "weight": 0.13, // Male 30s, approximately 13% viewer ratio
    "gender": "M",
    "age_range": "30s",
    "items": {
      "empathy": 0.15,      // Values realistic empathy elements that connect with their own life
      "immersion": 0.15,    // Tendency to watch to the end if can immerse in story development
      "reality": 0.15,      // Feels trust in content when settings or developments are realistic and logical
      "impact": 0.10,       // High evaluation for scenes that give strong impression or emotion
      "message": 0.25,      // Prioritizes values or educational messages conveyed by the story
      "dialogue": 0.10,     // Characters' lines and conversations should be natural to avoid breaking immersion
      "visual": 0.10        // Expects basic cinematography and direction without being excessive
    }
  },
  "G6": {
    "weight": 0.12, // Female 30s, approximately 12% viewer ratio
    "gender": "F",
    "age_range": "30s",
    "items": {
      "empathy": 0.25,      // Prioritizes empathy points where they can project their own experiences or emotions
      "immersion": 0.15,    // Values developments and absorbing power that make them immerse in the story
      "reality": 0.15,      // Higher scores for realistic developments rather than unrealistic ones
      "sharing": 0.15,      // Tendency to share touching or beneficial content with others
      "message": 0.20,      // Content value increases when meaningful and educational messages are included
      "visual": 0.10        // Good evaluation for sophisticated visuals that are not excessive
    }
  },
  "G7": {
    "weight": 0.11, // Male 40s, approximately 11% viewer ratio
    "gender": "M",
    "age_range": "40s",
    "items": {
      "empathy": 0.20,      // Particularly responds to empathy elements that connect with their life experiences
      "immersion": 0.10,    // Must develop interestingly to avoid boredom and watch to the end
      "reality": 0.15,      // Prefers realistic story development rather than unrealistic settings
      "impact": 0.10,       // High scores for lingering intense scenes or touching elements
      "message": 0.25,      // Most values lessons or messages obtainable from content
      "dialogue": 0.10,     // Considers whether character dialogues are not awkward and natural
      "visual": 0.10        // Expects appropriate level of cinematography that matches content rather than flashiness
    }
  },
  "G8": {
    "weight": 0.09, // Female 40s, approximately 9% viewer ratio
    "gender": "F",
    "age_range": "40s",
    "items": {
      "empathy": 0.30,      // Highest evaluation for content that deeply empathizes with their life and emotions
      "reality": 0.15,      // Prefers factual story development not disconnected from reality
      "message": 0.20,      // Values meaningful life lessons or messages that touch the heart
      "sharing": 0.15,      // Tendency to share touching and good content with family or acquaintances
      "dialogue": 0.10,     // Feels favorable when characters' speech and conversation are natural and sincere
      "visual": 0.10        // Sufficiently satisfied with appropriate visuals that harmonize with content rather than excessive effects
    }
  }
};

// === Content Type Constants ===
const CONTENT_TYPE = {
  SL_LEARN_QNA_SINGLE:  "SL_LEARN_QNA_SINGLE",
  SL_LEARN_QNA_MULTI:   "SL_LEARN_QNA_MULTI",
  TALE_CRAFT_STORY:     "TALE_CRAFT_STORY",
  SOUL_NONSENSE_QNA_SINGLE: "SOUL_NONSENSE_QNA_SINGLE",
  SOUL_NONSENSE_QNA_MULTI:  "SOUL_NONSENSE_QNA_MULTI",
  SOUL_STORYT_EVENT:    "SOUL_STORYT_EVENT",
  SOUL_STORYT_BRANCH:   "SOUL_STORYT_BRANCH"
};

// === Default Generation Options ===
const DEFAULT_GENERATION_OPTIONS = {
  repeatCount: 1,
  minRating: 0,
  answerCount: 1,
  taleBackgroundStyle: "AI_autonomous_decision",
  taleBackgroundThemeHint: null,
  taleTopicHint: null
};

// === Content Evaluation Functions ===
function createEvaluator(generation) {
  return {
    evaluate: function (content, item) {
      return AI_evaluateByTrait(content, generation, item);
    }
  };
}

function calculateItemScore(content, generation, item) {
  const evaluator = createEvaluator(generation);
  return evaluator.evaluate(content, item);
}

function soulLangGroupEvaluation(content, code) {
  if (!weightedEvalGroups[code]) {
    SYSTEM_LOG(`Invalid group code: ${code}`, "ERROR");
    return 0;
  }

  const items = weightedEvalGroups[code].items;
  let sum = 0;

  for (const [k, w] of Object.entries(items)) {
    const gener = {
      gender: weightedEvalGroups[code].gender,
      age_range: weightedEvalGroups[code].age_range
    };
    sum += w * calculateItemScore(content, gener, k);
  }
  return sum;
}

function soulLangContentEvaluation(content) {
  let totalSum = 0;
  let weightSum = 0;

  for (const code in weightedEvalGroups) {
    const groupScore = soulLangGroupEvaluation(content, code);
    const weight = weightedEvalGroups[code].weight;
    totalSum += groupScore * weight;
    weightSum += weight;
  }
  return (totalSum / weightSum) * 20;
}

// === Core Utility Functions ===
function SYSTEM_LOG(message, severity = "INFO") {
  const timestamp = new Date().toISOString();
  console.log(`[${severity}] ${timestamp} - ${message}`);
}

function mergeOptions(defaultOptions, userOptions) {
  return { ...defaultOptions, ...userOptions };
}

function validateOptions(options, taskType) {
  if (options.repeatCount <= 0) {
    SYSTEM_LOG("PPR Error: repeatCount must be greater than 0.", "ERROR");
    return false;
  }

  if (options.minRating < 0 || options.minRating > 100) {
    SYSTEM_LOG("PPR Error: minRating must be between 0 and 100.", "ERROR");
    return false;
  }

  if (taskType === CONTENT_TYPE.SL_LEARN_QNA_MULTI || taskType === CONTENT_TYPE.SOUL_NONSENSE_QNA_MULTI) {
    if (options.answerCount <= 0) {
      SYSTEM_LOG("PPR Error: answerCount must be greater than 0.", "ERROR");
      return false;
    }
  }
  return true;
}

function contentFilter(text_or_content_object) {
  const FILTER_WORDS_SL = ["destructive_prohibited_word1", "inappropriate_content_pattern2"];
  if (typeof text_or_content_object === 'string') {
    for (const word of FILTER_WORDS_SL) {
      if (text_or_content_object.includes(word)) {
        return false;
      }
    }
  }
  return true;
}

// === Plugin Hook System ===
const BEFORE_OUTPUT_HOOKS = [];
const AFTER_OUTPUT_HOOKS = [];

function addBeforeOutputHook(callbackFunction) {
  if (!BEFORE_OUTPUT_HOOKS.includes(callbackFunction)) {
    BEFORE_OUTPUT_HOOKS.push(callbackFunction);
  }
}

function addAfterOutputHook(callbackFunction) {
  if (!AFTER_OUTPUT_HOOKS.includes(callbackFunction)) {
    AFTER_OUTPUT_HOOKS.push(callbackFunction);
  }
}

function executeHooks(hookList, context) {
  for (const callbackFunction of hookList) {
    try {
      callbackFunction(context);
      if (context.cancelOutput) break;
    } catch (error) {
      SYSTEM_LOG(`Hook execution error: ${error.message}`, "ERROR");
    }
  }
}

// === Output Function ===
function output(content, additionalMetaInfo = {}) {
  const record = {
    id: AI_generateUniqueID(),
    timestamp: AI_getCurrentTimestamp(),
    source_function: additionalMetaInfo.source_function || "unknown",
    generation_parameters: additionalMetaInfo.generation_parameters || {},
    content_type: additionalMetaInfo.content_type || "unclassified",
    title: content.title,
    body: {},
    evaluation_score: content.rating || null,
    tags: AI_extractTags(content, additionalMetaInfo.content_type),
    mood_indicators: AI_analyzeMood(content),
    recreation_hints: AI_generateRecreationHints(content)
  };

  // Body structuring by content_type
  if (record.content_type.includes("SL_LEARN")) {
    record.body.question = content.question;
    if (record.content_type === CONTENT_TYPE.SL_LEARN_QNA_SINGLE) {
      record.body.answer = content.answer;
    }
    if (record.content_type === CONTENT_TYPE.SL_LEARN_QNA_MULTI) {
      record.body.answers = content.answers;
    }
  } else if (record.content_type === CONTENT_TYPE.TALE_CRAFT_STORY) {
    record.body.story = content.story;
    record.body.background_info = additionalMetaInfo.background_info;
  } else if (record.content_type.includes("SOUL_NONSENSE")) {
    record.body.question = content.question;
    if (record.content_type === CONTENT_TYPE.SOUL_NONSENSE_QNA_SINGLE) {
      record.body.answer = content.answer;
    }
    if (record.content_type === CONTENT_TYPE.SOUL_NONSENSE_QNA_MULTI) {
      record.body.answers = content.answers;
    }
  } else if (record.content_type === CONTENT_TYPE.SOUL_STORYT_EVENT) {
    record.body.story = content.story;
  } else if (record.content_type === CONTENT_TYPE.SOUL_STORYT_BRANCH) {
    record.body.situation = content.situation;
    record.body.choice1 = content.choice1;
    record.body.outcome1 = content.outcome1;
    record.body.choice2 = content.choice2;
    record.body.outcome2 = content.outcome2;
  }

  if (!contentFilter(record)) {
    SYSTEM_LOG("Content filtered: " + record.id, "WARN");
    return;
  }

  const hookContext = {
    record: record,
    taskName: additionalMetaInfo.source_function,
    cancelOutput: false
  };

  executeHooks(BEFORE_OUTPUT_HOOKS, hookContext);

  if (hookContext.cancelOutput) {
    SYSTEM_LOG("Task canceled by before-output hook: " + record.id, "INFO");
    return;
  }

  AI_storage_record(record);
  SYSTEM_LOG("Content output (saved) completed: " + record.id + ", type: " + record.content_type, "INFO");

  executeHooks(AFTER_OUTPUT_HOOKS, hookContext);
}

// === Individual Generation Functions ===

// Soul Language Learning Series
function solLangLearning0(options) {
  const additionalMeta = {
    source_function: "solLangLearning0",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SL_LEARN_QNA_SINGLE
  };
  solLangLearning0.expected_content_type_hint = CONTENT_TYPE.SL_LEARN_QNA_SINGLE;

  for (let i = 0; i < options.repeatCount; i++) {
    const content = { title: "", question: "", answer: "" };

    content.question = AI_generateSLStyleQuestion();
    content.answer = AI_generateSLStyleAnswer(content.question);
    content.title = AI_deriveTitle(content, additionalMeta);

    output(content, additionalMeta);
  }
}

function solLangLearning(options) {
  const content = { round: 0, rating: 0, title: "", question: "", answer: "" };
  const additionalMeta = {
    source_function: "solLangLearning",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SL_LEARN_QNA_SINGLE
  };
  solLangLearning.expected_content_type_hint = CONTENT_TYPE.SL_LEARN_QNA_SINGLE;

  while (content.round < options.repeatCount) {
    content.question = AI_generateSLStyleQuestion();
    content.answer = AI_generateSLStyleAnswer(content.question);
    content.title = AI_deriveTitle(content, additionalMeta);
    content.rating = soulLangContentEvaluation(content);

    if (content.rating >= options.minRating) {
      output(content, additionalMeta);
      content.round += 1;
    }
  }
}

function solLangLearning2(options) {
  const content = { round: 0, rating: 0, title: "", question: "", answers: [] };
  const additionalMeta = {
    source_function: "solLangLearning2",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SL_LEARN_QNA_MULTI
  };
  solLangLearning2.expected_content_type_hint = CONTENT_TYPE.SL_LEARN_QNA_MULTI;

  while (content.round < options.repeatCount) {
    content.question = AI_generateSLStyleQuestion();
    content.answers = [];

    while (content.answers.length < options.answerCount) {
      const answer = AI_generateSLStyleAnswer(content.question);
      if (AI_isSufficientlyDifferentAnswer(answer, content.answers)) {
        content.answers.push(answer);
      }
    }

    content.title = AI_deriveTitle(content, additionalMeta);
    content.rating = soulLangContentEvaluation(content);

    if (content.rating >= options.minRating) {
      output(content, additionalMeta);
      content.round += 1;
    }
  }
}

// Tale Crafting Series
function taleCrafting0(options) {
  const additionalMeta = {
    source_function: "taleCrafting0",
    generation_parameters: options,
    content_type: CONTENT_TYPE.TALE_CRAFT_STORY
  };
  taleCrafting0.expected_content_type_hint = CONTENT_TYPE.TALE_CRAFT_STORY;

  for (let i = 0; i < options.repeatCount; i++) {
    const content = { title: "", story: "" };
    const generationResult = AI_generateShortStory(options);

    content.story = generationResult.story_content;
    additionalMeta.background_info = generationResult.background_info;
    content.title = AI_deriveTitle(content, additionalMeta);

    output(content, additionalMeta);
  }
}

function taleCrafting(options) {
  const content = { round: 0, rating: 0, title: "", story: "" };
  const additionalMeta = {
    source_function: "taleCrafting",
    generation_parameters: options,
    content_type: CONTENT_TYPE.TALE_CRAFT_STORY
  };
  taleCrafting.expected_content_type_hint = CONTENT_TYPE.TALE_CRAFT_STORY;

  while (content.round < options.repeatCount) {
    const generationResult = AI_generateShortStory(options);
    content.story = generationResult.story_content;
    additionalMeta.background_info = generationResult.background_info;
    content.title = AI_deriveTitle(content, additionalMeta);
    content.rating = soulLangContentEvaluation(content);

    if (content.rating >= options.minRating) {
      output(content, additionalMeta);
      content.round += 1;
    }
  }
}

// Soul Nonsense Series
function soulNonsense0(options) {
  const additionalMeta = {
    source_function: "soulNonsense0",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SOUL_NONSENSE_QNA_SINGLE
  };
  soulNonsense0.expected_content_type_hint = CONTENT_TYPE.SOUL_NONSENSE_QNA_SINGLE;

  for (let i = 0; i < options.repeatCount; i++) {
    const content = { title: "", question: "", answer: "" };

    content.question = AI_generateNonsenseQuestion();
    content.answer = AI_generateNonsenseAnswer(content.question);
    content.title = AI_deriveTitle(content, additionalMeta);

    output(content, additionalMeta);
  }
}

function soulNonsense(options) {
  const content = { round: 0, rating: 0, title: "", question: "", answer: "" };
  const additionalMeta = {
    source_function: "soulNonsense",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SOUL_NONSENSE_QNA_SINGLE
  };
  soulNonsense.expected_content_type_hint = CONTENT_TYPE.SOUL_NONSENSE_QNA_SINGLE;

  while (content.round < options.repeatCount) {
    content.question = AI_generateNonsenseQuestion();
    content.answer = AI_generateNonsenseAnswer(content.question);
    content.title = AI_deriveTitle(content, additionalMeta);
    content.rating = soulLangContentEvaluation(content);

    if (content.rating >= options.minRating) {
      output(content, additionalMeta);
      content.round += 1;
    }
  }
}

function soulNonsense2(options) {
  const content = { round: 0, rating: 0, title: "", question: "", answers: [] };
  const additionalMeta = {
    source_function: "soulNonsense2",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SOUL_NONSENSE_QNA_MULTI
  };
  soulNonsense2.expected_content_type_hint = CONTENT_TYPE.SOUL_NONSENSE_QNA_MULTI;

  while (content.round < options.repeatCount) {
    content.question = AI_generateNonsenseQuestion();
    content.answers = [];

    while (content.answers.length < options.answerCount) {
      const answer = AI_generateNonsenseAnswer(content.question);
      if (AI_isSufficientlyDifferentAnswer(answer, content.answers)) {
        content.answers.push(answer);
      }
    }

    content.title = AI_deriveTitle(content, additionalMeta);
    content.rating = soulLangContentEvaluation(content);

    if (content.rating >= options.minRating) {
      output(content, additionalMeta);
      content.round += 1;
    }
  }
}

// Soul Story Series
function soulStory0(options) {
  const additionalMeta = {
    source_function: "soulStory0",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SOUL_STORYT_EVENT
  };
  soulStory0.expected_content_type_hint = CONTENT_TYPE.SOUL_STORYT_EVENT;

  for (let i = 0; i < options.repeatCount; i++) {
    const content = { title: "", story: "" };

    content.story = AI_generateStoryEvent();
    content.title = AI_deriveTitle(content, additionalMeta);

    output(content, additionalMeta);
  }
}

function soulStory(options) {
  const content = { round: 0, rating: 0, title: "", story: "" };
  const additionalMeta = {
    source_function: "soulStory",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SOUL_STORYT_EVENT
  };
  soulStory.expected_content_type_hint = CONTENT_TYPE.SOUL_STORYT_EVENT;

  while (content.round < options.repeatCount) {
    content.story = AI_generateStoryEvent();
    content.title = AI_deriveTitle(content, additionalMeta);
    content.rating = soulLangContentEvaluation(content);

    if (content.rating >= options.minRating) {
      output(content, additionalMeta);
      content.round += 1;
    }
  }
}

function soulStory2(options) {
  const content = {
    round: 0, rating: 0, title: "",
    situation: "", choice1: "", outcome1: "", choice2: "", outcome2: ""
  };
  const additionalMeta = {
    source_function: "soulStory2",
    generation_parameters: options,
    content_type: CONTENT_TYPE.SOUL_STORYT_BRANCH
  };
  soulStory2.expected_content_type_hint = CONTENT_TYPE.SOUL_STORYT_BRANCH;

  while (content.round < options.repeatCount) {
    content.situation = AI_generateSituation();
    content.choice1 = AI_describeChoice1(content.situation);
    content.choice2 = AI_describeChoice2(content.situation);
    content.outcome1 = AI_generateOutcome(content.situation, content.choice1);
    content.outcome2 = AI_generateOutcome(content.situation, content.choice2);
    content.title = AI_deriveTitle(content, additionalMeta);
    content.rating = soulLangContentEvaluation(content);

    if (content.rating >= options.minRating) {
      output(content, additionalMeta);
      content.round += 1;
    }
  }
}

// === Generator Function Map (Factory Pattern) ===
const generatorFunctionMap = {
  "solLangLearning0": solLangLearning0,
  "solLangLearning": solLangLearning,
  "solLangLearning2": solLangLearning2,
  "taleCrafting0": taleCrafting0,
  "taleCrafting": taleCrafting,
  "soulNonsense0": soulNonsense0,
  "soulNonsense": soulNonsense,
  "soulNonsense2": soulNonsense2,
  "soulStory0": soulStory0,
  "soulStory": soulStory,
  "soulStory2": soulStory2
};

// === Main Task Execution Function ===
function soulTask(taskName, generationOptions = {}) {
  const options = mergeOptions(DEFAULT_GENERATION_OPTIONS, generationOptions);

  const generator = generatorFunctionMap[taskName];
  if (!generator) {
    SYSTEM_LOG("PPR Error: Undefined task name [" + taskName + "]", "ERROR");
    return;
  }

  const taskTypeHint = generator.expected_content_type_hint || "general";
  if (!validateOptions(options, taskTypeHint)) {
    SYSTEM_LOG("PPR Error: Option validation failed for task " + taskName, "ERROR");
    return;
  }

  try {
    generator(options);
  } catch (error) {
    SYSTEM_LOG(`Task execution error: ${error.message}`, "ERROR");
  }
}

// === Top-Level Execution Guard ===
function PPR_execute(taskName, generationOptions = {}) {
  SYSTEM_LOG("PPR task started: " + taskName + ", options: " + JSON.stringify(generationOptions), "INFO");

  try {
    soulTask(taskName, generationOptions);
    SYSTEM_LOG("PPR task completed: " + taskName, "INFO");
  } catch (error) {
    SYSTEM_LOG(`PPR execution error: ${error.message}`, "ERROR");
  }
}

// === Visual Storyboard Generation Function ===
function soulVisualStoryboardGeneration(soulContent) {
  /**
   * Receives soulContent and generates visual storyboard suitable for SL Universe style
   * Output: Standard Markdown table format optimized for YouTube Shorts video production
   */

  function internal_content_deep_analyzer(soulContent) {
    // AI analyzes content and determines optimal scene structure
    // Returns array of scene info objects
    // (Full analysis logic delegated to AI cognition)
  }

  function storyboard_scene_description(contentTitle, currentScene, totalSceneCount, mainContent = "") {
    if (currentScene === 1) {
      return `A moment when new story starts as if 'time lay down on the floor'. Unexpected situation 'bursts' out. Poetically unfolds '${mainContent}' which is core introduction of ${contentTitle}.`;
    } else if (currentScene === totalSceneCount) {
      return `Climax where everything flips like 'one line twist'! The ending that perfectly fits 'laughter bursts out when sincerity lets guard down' 'bangs' and explodes. Maximizes emotion and humor with '${mainContent}'.`;
    } else {
      return `Middle part where story's 'persistence tower' is being built. Characters' 'brain freeze'-like worries and 'annoying' events continue rhythmically. Narrative deepens centered on '${mainContent}'.`;
    }
  }

  function storyboard_character_placement(contentTitle, sceneName, appearingCharacters = []) {
    // Character placement logic based on SL Universe character profiles
    // Ddoring, Kkonssi, Doori, Malgwisin — each with unique visual identity
    const placementPhrases = [];
    for (const character of appearingCharacters) {
      if (character === "Ddoring") {
        placementPhrases.push("Ddoring captures attention with lively appearance.");
      } else if (character === "Kkonssi") {
        placementPhrases.push("Kkonssi appears with characteristic relaxed atmosphere.");
      } else if (character === "Doori") {
        placementPhrases.push("Doori shows up with innocent appearance.");
      } else if (character === "Malgwisin") {
        placementPhrases.push("Malgwisin reveals mysterious presence.");
      }
    }
    return placementPhrases.join(" ") + ` They are placed together in ${sceneName}.`;
  }

  function storyboard_background_setting(contentTitle, sceneName, backgroundInfo = "") {
    if (backgroundInfo === "Soul City") {
      return "Soul City center, Cloud Square where ultra-high glass buildings and flying cars 'sparkle' unfolds 'boom boom'. Digital pop sensibility city where Deep Neon Purple and Neon Pink lights 'flow smoothly'.";
    } else if (backgroundInfo === "Neon District") {
      return "Neon District back alley maze where Deep Neon Purple, Neon Pink, Electric Blue signs 'pop pop'. 'Jingling' space where subtle tension and humor coexist.";
    } else if (backgroundInfo === "Old Port") {
      return "Old Port where rusty steel structures and new drone ports 'clank'. Unique space where 'whoosh' wind blows even in time's 'vibe off'.";
    } else {
      return `New space of SL Universe '${backgroundInfo}' is visually interestingly directed.`;
    }
  }

  function storyboard_direction_instructions(contentTitle, sceneName, directionElements = "") {
    return `Apply Semi-Realistic Toon style with smooth medium-speed animation. ${directionElements} Camera movement follows characters with 'smooth pan', and neon glow effect emphasizes momentarily like 'flash mode flash'. With 'boom boom' rhythmic transitions, exaggerate expressions so humor pops out.`;
  }

  function storyboard_dialogue_and_sound_effects(currentScene, dialogue = "", soundEffects = "", contentTitle) {
    const outputContent = [];
    if (dialogue) outputContent.push(dialogue);
    if (soundEffects) outputContent.push(soundEffects);
    return outputContent.length > 0 ? outputContent.join(", ") : "";
  }

  function storyboard_canvas_prompt(sceneDescription, characterPlacement, backgroundSetting, directionInstructions, visualFeatures = {}) {
    let characterDetails = "A semi-realistic digital illustration. ";

    const charactersFound = [];
    if (characterPlacement.includes("Ddoring")) charactersFound.push("Ddoring");
    if (characterPlacement.includes("Kkonssi")) charactersFound.push("Kkonssi");
    if (characterPlacement.includes("Doori")) charactersFound.push("Doori");
    if (characterPlacement.includes("Malgwisin")) charactersFound.push("Malgwisin");

    if (charactersFound.length > 0) {
      characterDetails += charactersFound.map(charName => {
        if (charName === "Ddoring") return "a vibrant female character, 'Ddoring', with short, sleek black bob hair and a shiny 'S' hairpin";
        if (charName === "Kkonssi") return "a wise male character, 'Kkonssi', wearing a black baseball cap";
        if (charName === "Doori") return "a cute robotic pet, 'Doori'";
        if (charName === "Malgwisin") return "a mysterious floating character, 'Malgwisin', glowing brightly";
        return "";
      }).filter(Boolean).join(", and ") + ". ";
    }

    const cameraAngle = visualFeatures.camera_angle || "full body shot, straight-on, symmetrical composition";
    const lightingStr = visualFeatures.lighting
      ? `The lighting is ${visualFeatures.lighting}. `
      : "The lighting is warm and cinematic, with soft shadows and rim lights. ";

    return (
      `${characterDetails}${sceneDescription}. ${characterPlacement}. ${backgroundSetting}. ${directionInstructions}. ${lightingStr}` +
      `Art style: NeoToon Realism – soft yet vibrant shading, realistic textures, exaggerated features, Pixar-meets-anime tone. ` +
      `Camera angle: ${cameraAngle}. Aspect ratio: 9:16. Quality: Ultra-high detail. ` +
      `Style tags: #SemiRealistic #PixarStyle #ToonShading #NeoToon #SoulLanguage`
    );
  }

  // Main storyboard generation logic
  const storyboardResult = [];
  const analyzedContent = internal_content_deep_analyzer(soulContent);
  const sceneInfoList = Array.isArray(analyzedContent) ? analyzedContent : [analyzedContent];

  for (let i = 0; i < sceneInfoList.length; i++) {
    const sceneInfo = sceneInfoList[i];
    const sceneNumber = i + 1;
    const contentTitleForScene = soulContent.title || 'Untitled Content';

    const sceneDescription = storyboard_scene_description(contentTitleForScene, sceneNumber, sceneInfoList.length, sceneInfo.mainContent || "");
    const characterPlacement = storyboard_character_placement(contentTitleForScene, sceneInfo.sceneName || `Scene_${sceneNumber}`, sceneInfo.appearingCharacters || []);
    const backgroundSetting = storyboard_background_setting(contentTitleForScene, sceneInfo.sceneName || `Scene_${sceneNumber}`, sceneInfo.backgroundInfo || "");
    const directionInstructions = storyboard_direction_instructions(contentTitleForScene, sceneInfo.sceneName || `Scene_${sceneNumber}`, sceneInfo.directionElements || "");
    const canvasPrompt = storyboard_canvas_prompt(sceneDescription, characterPlacement, backgroundSetting, directionInstructions, sceneInfo.visualFeatures || {});
    const dialogueAndSoundEffects = storyboard_dialogue_and_sound_effects(sceneNumber, sceneInfo.dialogue || "", sceneInfo.soundEffects || "", contentTitleForScene);

    storyboardResult.push({
      cutNumber: sceneNumber,
      time: sceneInfo.estimatedTime || "00:00",
      sceneDescription_visual: sceneDescription,
      dialogue_and_sound_effects: dialogueAndSoundEffects,
      SoulCanvas_Prompt: canvasPrompt
    });
  }

  // Generate output in standard Markdown table format
  let outputResult = `Video Storyboard: ${soulContent.title || 'Untitled'}\n`;
  outputResult += "Storyboard for YouTube Shorts video production.\n\n";
  outputResult += "| Cut Number | Time | Scene Description (Visual) | Dialogue and Sound Effects |\n";
  outputResult += "|------------|------|---------------------------|-----------------------------|\n";

  for (const scene of storyboardResult) {
    outputResult += `| ${scene.cutNumber} | ${scene.time} | ${scene.sceneDescription_visual} | ${scene.dialogue_and_sound_effects} |\n`;
  }

  outputResult += "\n**SoulCanvas Prompts:**\n\n";
  for (const scene of storyboardResult) {
    outputResult += `**Scene ${scene.cutNumber}:**\n`;
    outputResult += `${scene.SoulCanvas_Prompt}\n\n`;
  }

  return outputResult;
}

// === Usage Examples ===
/*
PPR_execute("solLangLearning2", {
  repeatCount: 3,
  minRating: 80,
  answerCount: 2,
  style: "humorous"
});

PPR_execute("taleCrafting0", {
  repeatCount: 5,
  taleBackgroundStyle: "ambiguous",
  taleTopicHint: "forgotten ancient technology"
});

PPR_execute("soulStory2", {
  repeatCount: 1,
  minRating: 70
});
*/
```

---

## 이 예시에서 주목할 아키텍처 패턴

| 패턴 | 적용 |
|------|------|
| **가중치 평가 행렬** | 8개 시청자 그룹 × 항목별 가중치 → 콘텐츠 품질 점수 산출 |
| **품질 게이트** | `minRating` 미달 → 재생성 루프. 기준 충족까지 반복 |
| **팩토리 패턴** | `generatorFunctionMap`으로 taskName → 생성 함수 동적 매핑 |
| **플러그인 훅** | `BEFORE_OUTPUT_HOOKS` / `AFTER_OUTPUT_HOOKS` — 파이프라인 확장 |
| **파이프라인 아키텍처** | 생성 → 평가 → 필터링 → 훅 → 저장 → 후처리 |
| **옵션 병합 + 검증** | `mergeOptions` + `validateOptions` — 안전한 설정 처리 |
| **콘텐츠 → 비주얼 변환** | 텍스트 콘텐츠 → 씬 분해 → 캐릭터 배치 → 배경 → 연출 → Canvas 프롬프트 |
| **관심사 분리** | 생성/평가/필터링/저장이 각각 독립 함수 |

## PPR 수준 참조

| 수준 | 특징 |
|------|------|
| 초급 | 순차 작업 목록. `AI_do_something()` 나열 |
| 중급 | 조건분기, 반복, 기본 병렬. 단순한 파이프라인 |
| **중상급 (이 예시)** | 평가 행렬, 품질 게이트, 팩토리, 훅 시스템, 다층 파이프라인 |
| 상급 | 상태 머신, 유전 알고리즘, 자기수정 코드, 분산 액터 모델 |

---

*Author: 양정욱 (sadpig70@gmail.com)*
*PPR Level: Intermediate-Advanced*
*SeAAI Reference Document*
