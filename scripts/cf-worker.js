const PATH_PREFIX = '/winterggg/github-issues-leetcode/pics/';

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url);
    url.host = 'raw.githubusercontent.com'
    url.pathname = PATH_PREFIX + url.pathname

    const modifiedRequest = new Request(url.toString(), {
        headers: request.headers,
        method: request.method,
        body: request.body,
        redirect: 'follow'
    });

    const response = await fetch(modifiedRequest);
    const modifiedResponse = new Response(response.body, response);

    // 添加允许跨域访问的响应头
    modifiedResponse.headers.set('Access-Control-Allow-Origin', '*');
    return modifiedResponse;
}