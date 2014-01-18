/* tes0.c
 * Copyright (C) 2008 梅濁酒 umedoblock
 */

#include <GL/gl.h>
#include <GL/glut.h>


void display(void)
{
    int pointSize = 4;

    glClear(GL_COLOR_BUFFER_BIT);

    glPointSize(pointSize);
    glBegin(GL_POINTS);
    glVertex2f(0 , -0.9);
    glEnd();

    glPointSize(pointSize*2);
    glBegin(GL_POINTS);
    glVertex2f(-0.9 , 0.9);
    glEnd();

    glPointSize(pointSize*4);
    glBegin(GL_POINTS);
    glVertex2f(0.9 , 0.9);
    glEnd();

    glFlush();
}
int main(int argc , char *argv[])
{
    int width, height, num;

    if (argc >= 2){
        num = atoi(argv[1]);
    }else{
        num = 500;
    }

    width = height = num;

    glutInit(&argc , argv);
    glutInitWindowPosition(0, 0);
    glutInitWindowSize(width, height);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA);

    glutCreateWindow(argv[0]);
    glutDisplayFunc(display);

    glutMainLoop();
    return 0;
}
