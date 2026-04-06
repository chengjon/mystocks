import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import * as ts from 'typescript'
import { HOME_ROUTE_PATH, LEGACY_HOME_ROUTE_PATH } from '@/router/homeRoute'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
const routerSourceFile = ts.createSourceFile('index.ts', routerSource, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)

const identifierPathMap: Record<string, string> = {
  HOME_ROUTE_PATH,
  LEGACY_HOME_ROUTE_PATH,
}

function readRouteString(node: ts.Expression | undefined): string | null {
  if (!node) {
    return null
  }

  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) {
    return node.text
  }

  if (ts.isIdentifier(node)) {
    return identifierPathMap[node.text] ?? null
  }

  return null
}

function getObjectProperty(
  node: ts.ObjectLiteralExpression,
  propertyName: string,
): ts.PropertyAssignment | undefined {
  return node.properties.find(
    (property): property is ts.PropertyAssignment =>
      ts.isPropertyAssignment(property)
      && ts.isIdentifier(property.name)
      && property.name.text === propertyName,
  )
}

function joinRoutePath(parentPath: string, ownPath: string): string {
  if (ownPath.startsWith('/')) {
    return ownPath
  }

  if (!parentPath || parentPath === '/') {
    return `/${ownPath}`.replace(/\/+/g, '/')
  }

  return `${parentPath.replace(/\/$/, '')}/${ownPath}`.replace(/\/+/g, '/')
}

function collectRoutePaths(elements: readonly ts.Expression[], parentPath = ''): string[] {
  const paths: string[] = []

  for (const element of elements) {
    if (!ts.isObjectLiteralExpression(element)) {
      continue
    }

    const pathProperty = getObjectProperty(element, 'path')
    const ownPath = readRouteString(pathProperty?.initializer)
    const fullPath = ownPath ? joinRoutePath(parentPath, ownPath) : null

    if (fullPath) {
      paths.push(fullPath)
    }

    const aliasProperty = getObjectProperty(element, 'alias')
    if (aliasProperty) {
      if (ts.isArrayLiteralExpression(aliasProperty.initializer)) {
        for (const aliasNode of aliasProperty.initializer.elements) {
          const alias = readRouteString(aliasNode)
          if (alias) {
            paths.push(joinRoutePath(parentPath, alias))
          }
        }
      } else {
        const alias = readRouteString(aliasProperty.initializer)
        if (alias) {
          paths.push(joinRoutePath(parentPath, alias))
        }
      }
    }

    const childrenProperty = getObjectProperty(element, 'children')
    if (childrenProperty && ts.isArrayLiteralExpression(childrenProperty.initializer)) {
      paths.push(...collectRoutePaths(childrenProperty.initializer.elements, fullPath || parentPath))
    }
  }

  return paths
}

function getRoutePathsFromRouterSource(): string[] {
  for (const statement of routerSourceFile.statements) {
    if (!ts.isVariableStatement(statement)) {
      continue
    }

    for (const declaration of statement.declarationList.declarations) {
      if (
        ts.isIdentifier(declaration.name)
        && declaration.name.text === 'routes'
        && declaration.initializer
        && ts.isArrayLiteralExpression(declaration.initializer)
      ) {
        return collectRoutePaths(declaration.initializer.elements)
      }
    }
  }

  return []
}

describe('router full path uniqueness', () => {
  it('keeps every routed full path unique across nested router truth', () => {
    const routePaths = getRoutePathsFromRouterSource()
    const duplicatePaths = [...new Set(routePaths.filter((path, index) => routePaths.indexOf(path) !== index))]

    expect(duplicatePaths).toEqual([])
  })

  it('keeps canonical dashboard and legacy compatibility paths distinct', () => {
    const routePaths = getRoutePathsFromRouterSource()

    expect(routePaths).toContain(HOME_ROUTE_PATH)
    expect(routePaths).toContain(LEGACY_HOME_ROUTE_PATH)
    expect(HOME_ROUTE_PATH).not.toBe(LEGACY_HOME_ROUTE_PATH)
  })
})
