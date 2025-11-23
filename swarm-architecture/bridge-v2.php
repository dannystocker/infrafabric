<?php
/**
 * Memory Exoskeleton Bridge v2.0 - Semantic Search Edition
 *
 * Provides HTTP API access to Redis data with semantic tagging and search
 *
 * New Features:
 * - Semantic tagging (topics, agents, content types)
 * - Full-text search across content
 * - Pattern-based filtering
 * - Statistics and analytics
 *
 * Endpoints:
 * - ?action=info          - System status and statistics
 * - ?action=keys          - List keys matching pattern
 * - ?action=batch         - Retrieve multiple keys with content
 * - ?action=tags          - Get semantic tags for keys
 * - ?action=search        - Semantic search by query
 * - ?action=health        - Health check
 *
 * Authentication: Bearer token required
 *
 * @version 2.0.0
 * @date 2025-11-23
 * @instance Instance #19 - Phase A
 */

// Configuration
define('BEARER_TOKEN', '50040d7fbfaa712fccfc5528885ebb9b');
define('DATA_FILE', __DIR__ . '/redis-data.json');
define('TAGS_FILE', __DIR__ . '/redis-semantic-tags.json');

// Redis Cloud (Predis) configuration
define('USE_REDIS_CLOUD', true);
define('REDIS_CLOUD_CONFIG', [
    'scheme' => 'tcp',
    'host' => 'redis-19956.c335.europe-west2-1.gce.cloud.redislabs.com',
    'port' => 19956,
    'username' => 'default',
    'password' => 'zYZUIwk4OVwPwG6fCn2bfaz7uROxmmI8'
]);

// CORS headers (allow Gemini-3-Pro web access)
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Authorization, Content-Type');
header('Content-Type: application/json');

// Handle OPTIONS preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Authentication
function authenticate() {
    $headers = getallheaders();
    $auth = $headers['Authorization'] ?? $headers['authorization'] ?? '';

    if ($auth !== 'Bearer ' . BEARER_TOKEN) {
        http_response_code(401);
        echo json_encode(['error' => 'Access Denied: Neural Link Severed']);
        exit;
    }
}

// Normalize data entries to the expected {id, content, ttl} shape
function normalize_entries($entries) {
    return array_map(function($entry) {
        $id = isset($entry['id']) ? $entry['id'] : ($entry['key'] ?? '');
        return [
            'id' => trim($id),
            'content' => $entry['content'] ?? ($entry['value'] ?? ''),
            'ttl' => $entry['ttl'] ?? null
        ];
    }, $entries);
}

// Load data files
function get_redis_client() {
    if (!USE_REDIS_CLOUD) return null;

    $autoload = __DIR__ . '/predis/autoload.php';
    if (!file_exists($autoload)) return null;

    require_once $autoload;

    try {
        return new Predis\Client(REDIS_CLOUD_CONFIG);
    } catch (Exception $e) {
        return null;
    }
}

function fetch_redis_data($client) {
    if ($client === null) return null;

    try {
        $keys = $client->keys('*');
        $entries = [];

        foreach ($keys as $key) {
            $value = $client->get($key);
            $ttl = $client->ttl($key);
            $entries[] = [
                'id' => $key,
                'content' => $value ?? '',
                'ttl' => $ttl
            ];
        }

        return [
            'batch_size' => count($entries),
            'data' => $entries,
            'source' => 'redis-cloud'
        ];
    } catch (Exception $e) {
        return ['error' => 'Redis cloud unavailable', 'detail' => $e->getMessage()];
    }
}

function load_data() {
    // Preferred: Redis Cloud backend via Predis
    $client = get_redis_client();
    $redis_data = fetch_redis_data($client);
    if ($redis_data !== null) {
        if (isset($redis_data['error'])) {
            $GLOBALS['redis_cloud_error'] = $redis_data['detail'] ?? 'unavailable';
        } else {
            $redis_data['data'] = normalize_entries($redis_data['data']);
            if (!isset($redis_data['batch_size'])) {
                $redis_data['batch_size'] = count($redis_data['data']);
            }
            if (!isset($redis_data['source'])) {
                $redis_data['source'] = 'redis-cloud';
            }
            return $redis_data;
        }
    }

    if (!file_exists(DATA_FILE)) {
        return ['error' => 'Data file not found', 'file' => DATA_FILE];
    }

    $content = file_get_contents(DATA_FILE);
    $data = json_decode($content, true);

    if ($data === null) {
        return ['error' => 'Invalid JSON in data file'];
    }

    // Handle legacy flat array exports ({key, value, ttl}[])
    if (is_array($data) && isset($data[0]) && isset($data[0]['key'])) {
        $normalized = normalize_entries($data);
        return [
            'batch_size' => count($normalized),
            'data' => $normalized,
            'source' => 'file-based'
        ];
    }

    // Preferred format: {"data": [{id, content, ttl}], ...}
    if (isset($data['data']) && is_array($data['data'])) {
        $data['data'] = normalize_entries($data['data']);
        if (!isset($data['batch_size'])) {
            $data['batch_size'] = count($data['data']);
        }
        if (!isset($data['source'])) {
            $data['source'] = 'file-based';
        }
        return $data;
    }

    return ['error' => 'Invalid data format', 'file' => DATA_FILE];
}

function load_tags() {
    if (!file_exists(TAGS_FILE)) {
        return null; // Tags are optional
    }

    $content = file_get_contents(TAGS_FILE);
    $tags_data = json_decode($content, true);

    if ($tags_data === null) {
        return null;
    }

    return $tags_data['tags'] ?? [];
}

// Convert Redis glob pattern to PHP regex
function glob_to_regex($pattern) {
    $pattern = str_replace('*', '.*', $pattern);
    $pattern = str_replace('?', '.', $pattern);
    return '/^' . $pattern . '$/';
}

// Filter keys by pattern
function filter_keys($keys, $pattern) {
    if ($pattern === '*' || empty($pattern)) {
        return $keys;
    }

    $regex = glob_to_regex($pattern);
    return array_filter($keys, function($key) use ($regex) {
        return preg_match($regex, $key);
    });
}

// Search content by query
function search_content($data, $query) {
    $query = strtolower(trim($query));
    $results = [];

    foreach ($data['data'] as $entry) {
        $key = $entry['id'];
        $content = strtolower($entry['content']);

        // Simple relevance scoring
        $score = 0;

        // Exact match in key
        if (stripos($key, $query) !== false) {
            $score += 10;
        }

        // Word match in content
        $words = explode(' ', $query);
        foreach ($words as $word) {
            if (strlen($word) < 3) continue;
            $count = substr_count($content, $word);
            $score += $count;
        }

        if ($score > 0) {
            $results[] = [
                'key' => trim($key),
                'score' => $score,
                'preview' => substr($entry['content'], 0, 200)
            ];
        }
    }

    // Sort by relevance
    usort($results, function($a, $b) {
        return $b['score'] - $a['score'];
    });

    return $results;
}

// Semantic search using tags
function semantic_search($tags, $data, $query) {
    $query = strtolower(trim($query));
    $results = [];

    foreach ($tags as $tag) {
        $score = 0;

        // Check topics
        foreach ($tag['topics'] as $topic) {
            if (stripos($topic, $query) !== false) {
                $score += 5;
            }
        }

        // Check agents
        foreach ($tag['agents'] as $agent) {
            if (stripos($agent, $query) !== false) {
                $score += 3;
            }
        }

        // Check content type
        if (stripos($tag['content_type'], $query) !== false) {
            $score += 4;
        }

        // Check status
        if (stripos($tag['status'], $query) !== false) {
            $score += 2;
        }

        // Check key
        if (stripos($tag['key'], $query) !== false) {
            $score += 10;
        }

        if ($score > 0) {
            $results[] = [
                'key' => $tag['key'],
                'score' => $score,
                'tags' => [
                    'topics' => $tag['topics'],
                    'agents' => $tag['agents'],
                    'type' => $tag['content_type'],
                    'status' => $tag['status']
                ]
            ];
        }
    }

    // Sort by relevance
    usort($results, function($a, $b) {
        return $b['score'] - $a['score'];
    });

    return $results;
}

// Main router
authenticate();

$action = $_GET['action'] ?? 'info';
$data = load_data();
if (!isset($data['source'])) {
    $data['source'] = USE_REDIS_CLOUD ? 'redis-cloud' : 'file-based';
}

if (isset($data['error'])) {
    http_response_code(500);
    echo json_encode($data);
    exit;
}

switch ($action) {
    case 'info':
        $tags = load_tags();
        $stats = [
            'status' => 'neural_link_active',
            'version' => '2.0.0',
            'backend' => $data['source'] ?? 'file-based',
            'keys_count' => count($data['data']),
            'semantic_tags_available' => $tags !== null,
            'capabilities' => [
                'pattern_matching' => true,
                'batch_retrieval' => true,
                'semantic_search' => $tags !== null,
                'full_text_search' => true
            ]
        ];

        if (isset($GLOBALS['redis_cloud_error'])) {
            $stats['redis_cloud_error'] = $GLOBALS['redis_cloud_error'];
        }

        if ($tags) {
            $stats['tag_statistics'] = [
                'total_tagged_keys' => count($tags),
                'unique_topics' => count(array_unique(array_merge(...array_column($tags, 'topics')))),
                'unique_agents' => count(array_unique(array_merge(...array_column($tags, 'agents'))))
            ];
        }

        echo json_encode($stats, JSON_PRETTY_PRINT);
        break;

    case 'keys':
        $pattern = $_GET['pattern'] ?? '*';
        $keys = array_map(function($entry) {
            return trim($entry['id']);
        }, $data['data']);

        $filtered = filter_keys($keys, $pattern);

        echo json_encode([
            'pattern' => $pattern,
            'count' => count($filtered),
            'keys' => array_values($filtered)
        ], JSON_PRETTY_PRINT);
        break;

    case 'batch':
        $pattern = $_GET['pattern'] ?? '*';
        $keys = array_map(function($entry) {
            return trim($entry['id']);
        }, $data['data']);

        $filtered_keys = filter_keys($keys, $pattern);

        $batch = array_filter($data['data'], function($entry) use ($filtered_keys) {
            return in_array(trim($entry['id']), $filtered_keys);
        });

        echo json_encode([
            'batch_size' => count($batch),
            'pattern' => $pattern,
            'data' => array_values($batch)
        ], JSON_PRETTY_PRINT);
        break;

    case 'tags':
        $tags = load_tags();
        if ($tags === null) {
            http_response_code(404);
            echo json_encode(['error' => 'Semantic tags not available']);
            break;
        }

        $pattern = $_GET['pattern'] ?? '*';
        $keys = array_map(function($entry) {
            return trim($entry['id']);
        }, $data['data']);

        $filtered_keys = filter_keys($keys, $pattern);

        $filtered_tags = array_filter($tags, function($tag) use ($filtered_keys) {
            return in_array($tag['key'], $filtered_keys);
        });

        echo json_encode([
            'pattern' => $pattern,
            'count' => count($filtered_tags),
            'tags' => array_values($filtered_tags)
        ], JSON_PRETTY_PRINT);
        break;

    case 'search':
        $query = $_GET['query'] ?? '';
        if (empty($query)) {
            http_response_code(400);
            echo json_encode(['error' => 'Query parameter required']);
            break;
        }

        $tags = load_tags();
        $semantic_flag = $_GET['semantic'] ?? 'true';
        $use_semantic = $semantic_flag !== 'false' && $tags !== null;

        if ($use_semantic) {
            $results = semantic_search($tags, $data, $query);
        } else {
            $results = search_content($data, $query);
        }

        $limit = intval($_GET['limit'] ?? 20);
        $results = array_slice($results, 0, $limit);

        echo json_encode([
            'query' => $query,
            'method' => $use_semantic ? 'semantic' : 'full-text',
            'count' => count($results),
            'results' => $results
        ], JSON_PRETTY_PRINT);
        break;

    case 'health':
        $health = [
            'status' => 'healthy',
            'data_file_exists' => file_exists(DATA_FILE),
            'data_file_size' => filesize(DATA_FILE),
            'tags_file_exists' => file_exists(TAGS_FILE),
            'timestamp' => date('c')
        ];

        echo json_encode($health, JSON_PRETTY_PRINT);
        break;

    default:
        http_response_code(400);
        echo json_encode([
            'error' => 'Invalid action',
            'valid_actions' => ['info', 'keys', 'batch', 'tags', 'search', 'health']
        ]);
        break;
}
?>
