const axios = require('axios');

test('API URL should return 200', async () => {
  const response = await axios.get('http://localhost:3000/api/data');
  expect(response.status).toBe(200);
});
