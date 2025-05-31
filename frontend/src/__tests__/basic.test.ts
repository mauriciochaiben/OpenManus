import { describe, test, expect } from 'vitest'

describe('Basic Test Suite', () => {
    test('should work with basic assertions', () => {
        expect(1 + 1).toBe(2)
        expect('hello').toBe('hello')
        expect(true).toBeTruthy()
    })

    test('should work with arrays', () => {
        const items = [1, 2, 3]
        expect(items).toHaveLength(3)
        expect(items).toContain(2)
    })

    test('should work with objects', () => {
        const user = { name: 'John', age: 30 }
        expect(user).toHaveProperty('name')
        expect(user.name).toBe('John')
    })
})
