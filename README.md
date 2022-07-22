# OAuth Playground

## Github OAuth Web

[github oauth](https://docs.github.com/cn/developers/apps/building-oauth-apps/authorizing-oauth-apps)

1. 服务端构建授权链接, 返回携带 `client_id` 和 `redirect_uri` 参数的 url, 由浏览器跳转到授权认证页面
2. 用户授权成功后, 跳转回`redirect_uri` 响应的页面
3. 在`redirect_uri`页面中, 通过 code, 像服务端换取 `access_token`
4. 通过`access_token`, 向 `github`获取`用户信息`

### 注意

1. 即使在授权链接的作用域内申明了 `user:email`,  在用户信息里拿到的`email`信息也可能是`null`
2. `code` 无法重复使用
